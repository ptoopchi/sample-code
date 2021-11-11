package group9;

import java.sql.Timestamp;
import java.text.SimpleDateFormat;
import java.util.Date;

/**
 * Fancy logger with various levels and different colours.
 * No external libraries required used.
 */
public class Log {

    /* Create a TAG variable like this at the top of
     * caller class. This makes it convenient to call
     * log methods without writing class name repeatedly.
     */
    private final static Class TAG = Log.class;

    /**
     * Showing example usage.
     *
     * @param args
     */
    public static void main(String[] args) {
        Log.d(TAG, "Meh");
        Log.i(TAG, "Hello");
        Log.w(TAG, "Whoa there!");
        Log.e(TAG, "Beep boop!");
    }

    // Date format.
    private static final SimpleDateFormat sdf = new SimpleDateFormat("yyyy.MM.dd.HH.mm.ss.SSS");

    // ANSI colours.
    private static final String ANSI_RESET = "\u001B[0m";
    private static final String ANSI_BLACK = "\u001B[30m";
    private static final String ANSI_RED = "\u001B[31m";
    private static final String ANSI_GREEN = "\u001B[32m";
    private static final String ANSI_YELLOW = "\u001B[33m";
    private static final String ANSI_BLUE = "\u001B[34m";
    private static final String ANSI_PURPLE = "\u001B[35m";
    private static final String ANSI_CYAN = "\u001B[36m";
    private static final String ANSI_WHITE = "\u001B[37m";

    /**
     * Log a message in blue to draw attention.
     *
     * @param c   The calling class.
     * @param msg The message to be written.
     */
    public static void a(Class c, String msg) {
        Timestamp timestamp = new Timestamp(System.currentTimeMillis());
        System.out.println(sdf.format(timestamp) + "  " + ANSI_BLUE + "ATTN" +
                "    [" + c.getName() + "]:  " + msg + ANSI_RESET);
    }

    /**
     * @param msg
     * @deprecated Replaced by {@code d(Class c, String msg)}
     */
    public static void d(String msg) {
        System.out.println(new Timestamp(new Date().getTime()) + "  " + "DEBUG" + ":  " + msg);
    }

    /**
     * Log a debug message. Also known as trace.
     *
     * @param c   The calling class.
     * @param msg The message to be written.
     */
    public static void d(Class c, String msg) {
        Timestamp timestamp = new Timestamp(System.currentTimeMillis());
        System.out.println(sdf.format(timestamp) + "  " + "DEBUG" + "   [" + c.getName() + "]:  " + msg);
    }

    /**
     * @param msg
     * @deprecated Replaced by {@code i(Class c, String msg)}
     */
    public static void i(String msg) {
        System.out.println(new Timestamp(new Date().getTime()) + "  " + ANSI_GREEN + "INFO" + ANSI_RESET + "    :  " + msg);
    }

    /**
     * Log a message to inform the user.
     *
     * @param c   The calling class.
     * @param msg The message to be written.
     */
    public static void i(Class c, String msg) {
        Timestamp timestamp = new Timestamp(System.currentTimeMillis());
        System.out.println(sdf.format(timestamp) + "  " + ANSI_GREEN + "INFO" + ANSI_RESET +
                "    [" + c.getName() + "]:  " + msg);
    }

    /**
     * @param msg
     * @deprecated Replaced by {@code w(Class c, String msg)}
     */
    public static void w(String msg) {
        System.out.println(new Timestamp(new Date().getTime()) + "  " + ANSI_YELLOW + "WARN" + ANSI_RESET + "    :  " + msg);
    }

    /**
     * Log a warning message.
     *
     * @param c   The calling class.
     * @param msg The message to be written.
     */
    public static void w(Class c, String msg) {
        Timestamp timestamp = new Timestamp(System.currentTimeMillis());
        System.out.println(sdf.format(timestamp) + "  " + ANSI_YELLOW + "WARN" +
                "    [" + c.getName() + "]:  " + msg + ANSI_RESET);
    }

    /**
     * @param msg
     * @deprecated
     */
    public static void e(String msg) {
        System.out.println(new Timestamp(new Date().getTime()) + "  " + ANSI_RED + "ERROR" + ANSI_RESET + "    :  " + msg);
    }

    /**
     * Log an error message.
     *
     * @param c   The calling class.
     * @param msg The message to be written.
     */
    public static void e(Class c, String msg) {
        Timestamp timestamp = new Timestamp(System.currentTimeMillis());
        System.out.println(sdf.format(timestamp) + "  " + ANSI_RED + "ERROR" + ANSI_RESET +
                "    [" + c.getName() + "]:  " + msg);
    }

}
