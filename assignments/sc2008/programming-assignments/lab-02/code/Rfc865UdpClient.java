import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.nio.charset.StandardCharsets;

public class Rfc865UdpClient {
    private static final int RFC865_PORT = 17;
    private static final int MAX_QUOTE_BYTES = 512;
    private static final int TIMEOUT_MILLISECONDS = 15_000;

    // A private course-submission copy should replace these placeholders:
    // Name: YourName
    // Group: YourLabGroup
    // IP Address: YourClientIPAddress

    public static void main(String[] args) {
        if (args.length < 2 || args.length > 3) {
            System.err.println(
                    "Usage: java Rfc865UdpClient <server-host> <request-text> [port]"
            );
            System.exit(1);
        }

        String serverHost = args[0];
        String requestText = args[1];
        int port = args.length == 3 ? parsePort(args[2]) : RFC865_PORT;

        try (DatagramSocket socket = new DatagramSocket()) {
            socket.setSoTimeout(TIMEOUT_MILLISECONDS);
            InetAddress serverAddress = InetAddress.getByName(serverHost);

            byte[] requestData =
                    requestText.getBytes(StandardCharsets.US_ASCII);
            DatagramPacket request = new DatagramPacket(
                    requestData,
                    requestData.length,
                    serverAddress,
                    port
            );
            socket.send(request);

            byte[] replyBuffer = new byte[MAX_QUOTE_BYTES];
            DatagramPacket reply =
                    new DatagramPacket(replyBuffer, replyBuffer.length);
            socket.receive(reply);

            String quote = new String(
                    reply.getData(),
                    reply.getOffset(),
                    reply.getLength(),
                    StandardCharsets.US_ASCII
            );
            System.out.println("Quote received: " + quote);
        } catch (Exception exception) {
            exception.printStackTrace();
        }
    }

    private static int parsePort(String value) {
        int port = Integer.parseInt(value);
        if (port < 1 || port > 65535) {
            throw new IllegalArgumentException("Port must be between 1 and 65535");
        }
        return port;
    }
}
