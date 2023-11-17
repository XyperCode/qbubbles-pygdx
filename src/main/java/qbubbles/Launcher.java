package qbubbles;

import org.python.apache.commons.compress.utils.IOUtils;
import org.python.core.PySystemState;
import org.python.util.PythonInterpreter;

import java.io.FileInputStream;
import java.io.IOException;
import java.net.URLConnection;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.jar.JarFile;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import java.util.zip.ZipInputStream;

public class Launcher {
    public static void main(String[] args) throws IOException {
        System.setProperty("python.import.site", "false");

        PythonInterpreter.initialize(null, null, args);
        PySystemState state = new PySystemState();
        Path tempDirectory = Files.createTempDirectory("qbubbles_");
        URLConnection connection = Launcher.class.getProtectionDomain().getCodeSource().getLocation().openConnection();
        try (var stream = new ZipInputStream(connection.getInputStream())) {
            ZipEntry entry;
            while ((entry = stream.getNextEntry()) != null) {
                copyEntry(entry, tempDirectory, stream);
            }
        }

        state.path.add(0, tempDirectory.toString());
        state.setClassLoader(ClassLoader.getSystemClassLoader());
        try (PythonInterpreter pythonInterpreter = new PythonInterpreter(null, state)) {
            pythonInterpreter.execfile(tempDirectory.resolve("main.py").toString());
        }
    }

    private static void copyEntry(ZipEntry entry, Path tempDirectory, ZipInputStream stream) throws IOException {
        if (entry.getName().endsWith(".py")) {
            String name = entry.getName();
            if (name.startsWith("/")) name = name.substring(1);
            if (name.equals("main.py") || name.startsWith("qbubbles/")) {
                var path = tempDirectory.resolve(name);
                if (Files.notExists(path.getParent())) {
                    Files.createDirectories(path.getParent());
                }
                byte[] bytes = stream.readAllBytes();
                Files.write(path, bytes, StandardOpenOption.TRUNCATE_EXISTING, StandardOpenOption.CREATE);
            }
        }
    }
}