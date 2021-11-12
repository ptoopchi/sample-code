import java.util.ArrayList;

public class Globals {
    /**
     * Empty Constructor.
     */
    public Globals() {
    }

    /**
     * Bit string.
     */
    static final int N = 40;
    static final int TWO_N = 2 * N;

    /**
     * Array to store random data noise.
     */
    static double[][] noiseTable = new double[N + 1][N + 1];

    /**
     * Min/Max values for random noise.
     */
    private double min = 0.5;
    private double max = 1.0;

    /**
     * Creates the random noise for the fitness function.
     */
    public void setupRandomNoise() {
        // Setup Random Noise for data
        for (int i = 0; i <= N; i++) {
            for (int j = 0; j <= N; j++) {
                noiseTable[i][j] = min + Math.random() * (max - min);
            }
        }
    }

    /**
     * Performs Mutation.
     *
     * @param individual_mutate_before - individual before mutation
     * @return - new mutated individual
     */
    public static int[] mutate(int[] individual_mutate_before) {
        int[] individual_mutate = individual_mutate_before.clone();

        for (int i = 0; i < individual_mutate.length; i++) {

            // Flip the bits
            if (Math.random() <= (1.0 / (2 * N))) {
                if (individual_mutate[i] == 1) {
                    individual_mutate[i] = 0;
                } else {
                    individual_mutate[i] = 1;
                }
            }
        }
        return individual_mutate;
    }

    /**
     * Create Population of individuals.
     *
     * @param size - size of population
     * @return population with size 'size'
     */
    public static ArrayList<Individual> createPopulation(int size) {
        ArrayList<Individual> population = new ArrayList<>();

        for (int i = 0; i < size; i++) {
            population.add(new Individual());
        }
        return population;
    }
}
