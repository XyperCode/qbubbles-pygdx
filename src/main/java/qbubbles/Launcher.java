package qbubbles;

import org.graalvm.polyglot.Context;
import org.graalvm.polyglot.Engine;
import org.graalvm.polyglot.Source;
import org.graalvm.polyglot.Value;

import java.io.IOException;
import java.io.InputStream;
import java.net.URL;

public class Launcher {

    public static final URL RESOURCE = Launcher.class.getResource("/main.py");

    public static void main(String[] args) throws IOException {
        if (RESOURCE == null) {
            throw new IOException("Resource not found");
        }

        try (Context ctx = Context.newBuilder("python").option("python.EmulateJython", "true").allowAllAccess(true).build()) {
            Value python = ctx.parse(Source.newBuilder("python", RESOURCE).name("main.py").build());
            Value result = python.execute();
        }
    }
}