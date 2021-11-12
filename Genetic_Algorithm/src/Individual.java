import java.util.Arrays;
import java.util.Random;
import java.util.stream.IntStream;

public class Individual {

    /**
     * The individuals bit string.
     */
    public int[] individual = new int[Globals.TWO_N];

    /**
     * Individuals fitness score.
     */
    public double fitness_score = 0;

    /**
     * Constructor.
     */
    public Individual() {
        // Create the individual
        makeIndividual();
        // Calculate the Fitness
        fitness_score = calculateFitness(individual);
    }

    /**
     * Randomly Sets the individual.
     */
    private void makeIndividual() {

        for (int i = 0; i < individual.length; i++) {
            // Random number ranges from 0 to 2 as nextInt() is not inclusive
            individual[i] = new Random().nextInt(2);
        }
    }

    /**
     * Calculates the fitness of an individual.
     *
     * @param individual_fit - the specific individual array
     * @return fitness score
     */
    public double calculateFitness(int[] individual_fit) {
        int count_i = 0;
        int count_j = 0;
        // Count the 1s in component i
        for (int i = 0; i < Globals.N; i++) {
            if (individual_fit[i] == 1) count_i++;
        }
        // Count the 1s in component j
        for (int i = Globals.N; i < Globals.TWO_N; i++) {
            if (individual_fit[i] == 1) count_j++;
        }
        // Return the count with random noise.
        double noise = Globals.noiseTable[count_i][count_j];
        return (noise * (Math.pow(2, count_i) + Math.pow(2, count_j)));
    }

    /**
     * Changes the individual bit string and recalculates fitness score.
     *
     * @param individual - the new individual
     */
    public void setIndividual(int[] individual) {
        this.individual = individual;
        this.fitness_score = calculateFitness(individual);
    }
}
