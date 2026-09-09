import java.io.InputStream;
import java.io.OutputStream;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

public class Rfc865TcpClient {
    private static final int RFC865_PORT = 17;
    private static final int MAX_QUOTE_BYTES = 512;
    private static final int TIMEOUT_MILLISECONDS = 5_000;

    public static void main(String[] args) {
        if (args.length < 2 || args.length > 3) {
            System.err.println(
                    "Usage: java Rfc865TcpClient <server-host> <request-text> [port]"
            );
            System.exit(1);
        }

        String serverHost = args[0];
        String requestText = args[1];
        int port = args.length == 3 ? parsePort(args[2]) : RFC865_PORT;

        try (Socket socket = new Socket(serverHost, port)) {
            socket.setSoTimeout(TIMEOUT_MILLISECONDS);

            OutputStream output = socket.getOutputStream();
            output.write(requestText.getBytes(StandardCharsets.US_ASCII));
            output.flush();

            InputStream input = socket.getInputStream();
            byte[] replyBuffer = new byte[MAX_QUOTE_BYTES];
            int replyLength = input.read(replyBuffer);
            if (replyLength < 0) {
                throw new IllegalStateException("Server closed without sending a quote");
            }

            String quote = new String(
                    replyBuffer,
                    0,
                    replyLength,
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
