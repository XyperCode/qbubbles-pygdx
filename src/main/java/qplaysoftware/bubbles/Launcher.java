package qplaysoftware.bubbles;

import org.python.core.PySystemState;
import org.python.util.PythonInterpreter;

public class Launcher {
    public static void main(String[] args) {
        System.setProperty("python.import.site", "false");

        PythonInterpreter.initialize(null, null, args);
        PySystemState state = new PySystemState();
        state.setClassLoader(ClassLoader.getSystemClassLoader());
        try (PythonInterpreter pythonInterpreter = new PythonInterpreter(null, state)) {
            pythonInterpreter.execfile(Launcher.class.getResourceAsStream("/main.py"));
        }
    }
}