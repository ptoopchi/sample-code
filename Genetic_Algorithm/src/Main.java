public class Main {
    public static void main(String[] args) {
        // Creates random static noise
        new Globals().setupRandomNoise();
        // Create GA with population size 100.
        new GAs(100).GAUniCrossover();
    }
}
