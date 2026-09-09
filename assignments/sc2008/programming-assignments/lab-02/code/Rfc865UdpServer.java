import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.nio.charset.StandardCharsets;

public class Rfc865UdpServer {
    private static final int RFC865_PORT = 17;
    private static final int MAX_QUOTE_BYTES = 512;

    public static void main(String[] args) {
        int port = args.length > 0 ? parsePort(args[0]) : RFC865_PORT;

        try (DatagramSocket socket = new DatagramSocket(port)) {
            System.out.println("RFC 865 UDP server listening on port " + port);

            while (true) {
                byte[] requestBuffer = new byte[MAX_QUOTE_BYTES];
                DatagramPacket request =
                        new DatagramPacket(requestBuffer, requestBuffer.length);
                socket.receive(request);

                byte[] quote =
                        "Programs must be written for people to read."
                                .getBytes(StandardCharsets.US_ASCII);
                DatagramPacket reply = new DatagramPacket(
                        quote,
                        quote.length,
                        request.getAddress(),
                        request.getPort()
                );
                socket.send(reply);

                System.out.printf(
                        "Replied to %s:%d%n",
                        request.getAddress().getHostAddress(),
                        request.getPort()
                );
            }
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
