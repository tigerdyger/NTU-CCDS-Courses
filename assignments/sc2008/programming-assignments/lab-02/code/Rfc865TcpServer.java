import java.io.OutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketTimeoutException;
import java.nio.charset.StandardCharsets;

public class Rfc865TcpServer {
    private static final int RFC865_PORT = 17;
    private static final int MAX_REQUEST_BYTES = 512;

    public static void main(String[] args) {
        int port = args.length > 0 ? parsePort(args[0]) : RFC865_PORT;

        try (ServerSocket serverSocket = new ServerSocket(port)) {
            System.out.println("RFC 865 TCP server listening on port " + port);

            while (true) {
                Socket clientSocket = serverSocket.accept();
                Thread thread = new Thread(() -> handleClient(clientSocket));
                thread.start();
            }
        } catch (Exception exception) {
            exception.printStackTrace();
        }
    }

    private static void handleClient(Socket socket) {
        try (socket) {
            System.out.printf(
                    "Connection from %s:%d%n",
                    socket.getInetAddress().getHostAddress(),
                    socket.getPort()
            );

            // RFC 865 ignores any data received from the client.
            socket.setSoTimeout(1_000);
            try {
                byte[] ignoredData = new byte[MAX_REQUEST_BYTES];
                socket.getInputStream().read(ignoredData);
            } catch (SocketTimeoutException ignored) {
                // A strictly RFC-compliant client may send no data.
            }

            byte[] quote =
                    "Programs must be written for people to read."
                            .getBytes(StandardCharsets.US_ASCII);
            OutputStream output = socket.getOutputStream();
            output.write(quote);
            output.flush();

            System.out.println("Quote sent");
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
