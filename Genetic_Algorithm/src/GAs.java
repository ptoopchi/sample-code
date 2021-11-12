import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Random;

public class GAs {

    /**
     * Size of the population.
     */
    int populationSize = 0;

    /**
     * Number of demes.
     */
    int demeSize = 100;

    /**
     * Max Score possible.
     */
    double maxScore = (Globals.noiseTable[Globals.N - 1][Globals.N - 1] * (Math.pow(2, Globals.N) + Math.pow(2, Globals.N)));

    /**
     * Best Fitness from deme for each generation.
     */
    ArrayList<Double> intrScores = new ArrayList<>();

    /**
     * Holds the Generation number.
     */
    ArrayList<Integer> intrScoresPOS = new ArrayList<>();

    /**
     * Stores all the demes populations.
     */
    ArrayList<ArrayList<Individual>> allDemes = new ArrayList<>();

    /**
     * Evaluations Counter.
     */
    int evals = 0;

    /**
     * Constructor.
     */
    public GAs(int size) {
        System.out.println("Running GA...");
        System.out.println("Top Score: " + maxScore);
        this.populationSize = size;
    }

    /**
     * Main function for performing GA with uniform crossover.
     *
     * @return (true = solution found) & (false = solution not found)
     */
    public Boolean GAUniCrossover() {
        // Evaluations counter
        evals = 0;

        // Create population of 100 individuals with 100 demes
        for (int i = 0; i < demeSize; i++) {
            ArrayList<Individual> array = Globals.createPopulation(populationSize);
            allDemes.add(array);
        }

        // Stores current best fitness
        double current_best = 0;

        while (true) {
            // We can see that GA with uniform crossover does not always reach the max score
            // Improvement can use a GA with one point crossover?
            // During testing it is set to 250 evaluations
            if (evals >= (250)) {
                System.out.println("[ INFO ] - No Solution Found!");
                return false;
            }
            if (current_best >= maxScore) {
                System.out.println("[ INFO ] - Fitness: " + current_best);
                System.out.println("[ INFO ] - Solution Found!");
                return true;
            }

            for (int i = 0; i < allDemes.size(); i++) {
                ArrayList<Individual> currentDeme = allDemes.get(i);

                ArrayList<Individual> nextEval = new ArrayList<>();
                // Create Next Eval
                // Elitism first then the rest of the population
                for (int j = 0; j < currentDeme.size() - 1; j++) {
                    Individual newOffSpring = new Individual();
                    int[] offSpring1 = selectParent(currentDeme).individual;
                    int[] offSpring2 = selectParent(currentDeme).individual;
                    int[] newSpring = uniformCrossover(offSpring1, offSpring2);
                    int[] mutateOffspring = combineMutation(newSpring);
                    newOffSpring.setIndividual(mutateOffspring);
                    nextEval.add(newOffSpring);
                }
                Individual best = getBestIndividual(currentDeme);
                nextEval.add(best);

                allDemes.set(i, nextEval);
                // Migration to another deme with probability of 0.0004
                if (Math.random() <= 0.0004) {
                    // Get random individual & Replace into deme
                    allDemes.get(new Random().nextInt(demeSize)).get(new Random().nextInt(populationSize)).setIndividual(best.individual);
                }
            }
            current_best = functionOutput(evals, allDemes);
            evals++;
        }
    }

    /**
     * Perform Uniform-Crossover.
     *
     * @param p1 - parent 1
     * @param p2 - parent 2
     * @return new individual from parents
     */
    public int[] uniformCrossover(int[] p1, int[] p2) {

        int[] new_individual = new int[Globals.TWO_N];

        for (int i = 0; i < p1.length; i++) {
            if (new Random().nextDouble() < 0.5) {
                new_individual[i] = p1[i];
            } else {
                new_individual[i] = p2[i];
            }
        }
        return new_individual;
    }

    /**
     * Combines the genotype and performs mutation.
     */
    public int[] combineMutation(int[] genetype) {
        int[] gene1 = Arrays.copyOfRange(genetype, 0, Globals.N);
        int[] gene2 = Arrays.copyOfRange(genetype, Globals.N, Globals.TWO_N);

        int[] gene1Mutate = Globals.mutate(gene1);
        int[] gene2Mutate = Globals.mutate(gene2);

        int[] newMutate = new int[Globals.TWO_N];

        for (int i = 0; i < newMutate.length; i++) {
            if (i < Globals.N) {
                newMutate[i] = gene1Mutate[i];
            } else {
                newMutate[i] = gene2Mutate[i - Globals.N];
            }
        }
        return newMutate;
    }

    /**
     * Get the best individual from population.
     *
     * @param population - the total population within deme
     * @return best individual from population
     */
    public Individual getBestIndividual(ArrayList<Individual> population) {
        Individual max_individual = null;
        double max_value = Integer.MIN_VALUE;

        for (int i = 0; i < population.size(); i++) {
            double score = population.get(i).calculateFitness(population.get(i).individual);
            if (score > max_value) {
                max_value = population.get(i).calculateFitness(population.get(i).individual);
                max_individual = population.get(i);
            }
        }
        return max_individual;
    }

    /**
     * Perform selection for parents based on weighting system.
     *
     * @param population - the total population within deme
     * @return a parent
     */
    public Individual selectParent(ArrayList<Individual> population) {
        Individual parent = null;

        double[] relativeProb = new double[populationSize];
        double cumulativeFreq = 0;
        double cumulativeWeights = 0;

        // Rank population based on fitness score.
        population.sort((p1, p2) -> {
            if (p1.fitness_score > p2.fitness_score) {
                return -1;
            } else if (p1.fitness_score < p2.fitness_score) {
                return 1;
            } else {
                return 0;
            }
        });

        // Each individual weighting is (popSize - i) [Best fitness gets highest weighting]
        // So i = 0 would be (10 - 0) = 10
        // i = 1 would be (10 - 1) = 9
        for (int i = 0; i < population.size(); i++) {
            cumulativeFreq += (populationSize - i);
            relativeProb[i] = ((populationSize - i));
        }

        double randNum = new Random().nextInt((int) cumulativeFreq);

        // Roulette wheel select parent
        for (int i = 0; i < relativeProb.length; i++) {
            cumulativeWeights += relativeProb[i];
            if (randNum < cumulativeWeights) {
                parent = population.get(i);
                break;
            }
        }
        return parent;
    }

    /**
     * Handles the printing of each Generation.
     *
     * @param eval -  number of evaluations
     * @return the best fitness for this given generation
     */
    private Double functionOutput(int eval, ArrayList<ArrayList<Individual>> allDemes) {

        // Get best individual from each deme
        ArrayList<Double> bestScores = new ArrayList<>();
        for (int i = 0; i < allDemes.size(); i++) {
            bestScores.add(getBestIndividual(allDemes.get(i)).fitness_score);
        }
        // Get the best overall individual
        double best = Collections.max(bestScores);
        System.out.println("[ INFO ] - Fitness: " + best + " in eval " + eval);
        intrScores.add(Collections.max(bestScores));
        intrScoresPOS.add(eval);
        return best;
    }
}
