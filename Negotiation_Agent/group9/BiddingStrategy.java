package group9;

import genius.core.Bid;
import genius.core.Domain;
import genius.core.issue.Issue;
import genius.core.issue.IssueDiscrete;
import genius.core.issue.Value;
import genius.core.issue.ValueDiscrete;
import genius.core.utility.AbstractUtilitySpace;
import genius.core.utility.AdditiveUtilitySpace;

import java.util.*;

/**
 * Class for Agent bidding Strategy.
 */
public class BiddingStrategy {

    // Used by logger.
    final static Class TAG = BiddingStrategy.class;

    private Double agentUtility;

    private AbstractUtilitySpace utilitySpace;

    private Domain domain;

    //before it was 0.08
    private final double SLACK = 0.08;


    /**
     * Constructor of class.
     */
    public BiddingStrategy(Double agentUtility, AbstractUtilitySpace utilitySpace, Domain domain) {
        this.agentUtility = agentUtility;
        this.utilitySpace = utilitySpace;
        this.domain = domain;
    }

    /**
     * Creates a bid using Bidding Strategy One.
     *
     * @return a bid for algorithm one
     */
    public Bid getBidFirstAlgorithm(List<Issue> issues, Bid bestUtilityBid, AdditiveUtilitySpace additiveUtilitySpace) {
        LinkedHashMap<Issue, Double> issueWeights = getAgentWeights(true, issues, additiveUtilitySpace);

        Bid randomBid = getBestBidFromSampleAlgoOne(bestUtilityBid, issueWeights);

        return randomBid;
    }

    /**
     * @return random issue from the list domain.
     */
    private Issue getRandomIssue(LinkedHashMap<Issue, Double> issueWeights) {
        // Random number between 0 to 1.
        double rand = Math.random();

        double cumulativeValue = 0d;

        Issue issueSelected = issueWeights.keySet().iterator().next();

        for (Issue key : issueWeights.keySet()) {
            cumulativeValue += issueWeights.get(key);
            if (rand < cumulativeValue) {
                issueSelected = key;
                break;
            }
        }

        return issueSelected;
    }

    /**
     * From the randomly selected issue a random variable is selected.
     *
     * @return a random valueDiscrete
     */
    private ValueDiscrete getRandomisedIssueVariable(Issue issue) {

        IssueDiscrete issueDiscrete = (IssueDiscrete) issue;

        int index = new Random().nextInt(issueDiscrete.getValues().size());

        return issueDiscrete.getValues().get(index);
    }

    /**
     * Create a Bid with variable randomised in the chosen issue.
     *
     * @return new bid
     */
    private Bid getBidFromRandomVariable(Bid bestBid, Issue issue, ValueDiscrete randomVariable) {

        HashMap<Integer, Value> map = bestBid.getValues();
        map.put(issue.getNumber(), randomVariable);
        return new Bid(domain, map);
    }

    /**
     * Creates a sample of bids greater than the target utility.
     * The best bid of the sample is returned.
     *
     * @return the max utility bid
     */
    private Bid getBestBidFromSampleAlgoOne(Bid bestBid, LinkedHashMap<Issue, Double> issueWeights) {

        Issue issue = getRandomIssue(issueWeights);

        // Loop through the variables of the issue and pick a random one
        ValueDiscrete valueDiscrete = getRandomisedIssueVariable(issue);

        Bid randomBid = getBidFromRandomVariable(bestBid, issue, valueDiscrete);
        // Check if its greater than our agent utility.
        if (utilitySpace.getUtility(randomBid) >= agentUtility) {
            return randomBid;
        }
        return bestBid;
    }


    /**
     * Standardise a Map.
     *
     * @return Standardised map
     */
    public LinkedHashMap<Issue, Double> standardiseMap(LinkedHashMap<Issue, Double> map) {
        double sumValue = 0d;

        // Get Sum
        for (Issue key : map.keySet()) {
            sumValue += map.get(key);
        }

        for (Issue key : map.keySet()) {
            map.put(key, (map.get(key) / sumValue));
        }
        return map;
    }

    /**
     * Creates a map which stores the issues and the weight for our agent
     * The boolean controls whether returned map weight is inverse.
     *
     * @return map which is standardised.
     */
    private LinkedHashMap<Issue, Double> getAgentWeights(Boolean inverse, List<Issue> issues, AdditiveUtilitySpace additiveUtilitySpace) {
        LinkedHashMap<Issue, Double> issueWeights = new LinkedHashMap<>();

        // Find the weights for all issues and store in map.
        for (int i = 0; i < issues.size(); i++) {
            Issue issue = issues.get(i);

            // Gets the issue name and its (1/weights) into the map.
            // This is (1/weight) as we want to get smaller weights to larger values
            // And larger weights to smaller values.
            if (!inverse) issueWeights.put(issue, additiveUtilitySpace.getWeight(issue.getNumber()));
            else issueWeights.put(issue, (1 / additiveUtilitySpace.getWeight(issue.getNumber())));
//            Log.w(TAG, "Inside getAgentWeights: " + additiveUtilitySpace.getWeight(issue.getNumber()));
        }

        //standardiseMap the issueWeights Map.
        return standardiseMap(issueWeights);
    }

    /**
     * Creates a bid using Bidding Strategy Two. 
     *
     * @return a bid for algorithm two
     */
    public Bid getBidSecondAlgorithm(List<Issue> issues, Bid opponentBid, AdditiveUtilitySpace additiveUtilitySpace) {
        LinkedHashMap<Issue, Double> issueWeights = getAgentWeights(false, issues, additiveUtilitySpace);

        Bid randomBid = null;

        // Counts the size of issueWeights
        int loopCounter = issueWeights.size();

        // Making a local copy of the issueWeights
        LinkedHashMap<Issue, Double> copyIssueWeights = new LinkedHashMap<>();
        for (Issue newKey : issueWeights.keySet()) {
            copyIssueWeights.put(newKey, issueWeights.get(newKey));
        }


        for (int i = 0; i < loopCounter; i++) {
            Issue issue = getRandomIssue(copyIssueWeights);

            for (int j = 0; j < 100; j++) {
                // Loop through the variables of the issue and pick a random one
                ValueDiscrete valueDiscrete = getRandomisedIssueVariable(issue);

                randomBid = getBidFromRandomVariable(opponentBid, issue, valueDiscrete);
                // Check if its greater than our agent utility.
                if (utilitySpace.getUtility(randomBid) >= (agentUtility - SLACK)) {
                    return randomBid;
                } else {
                    // If the randomBid is not greater we set to null so that we can
                    // Move on to algo3
                    randomBid = null;
                }
            }

            copyIssueWeights.remove(issue);
        }

        return randomBid;
    }

    /**
     * Returns a list of the issue name most wanted by the opponent and the variable name.
     */
    private String[] getMostWantedOpponentIssue(List<IssueTable> issueTable) {

        Map.Entry<String, Integer> highestOpponentVariable = issueTable.get(0)
                .getVariablesFreqTable().entrySet().iterator().next();

        String highestIssueName = "";

        for (int i = 0; i < issueTable.size(); i++) {

            IssueTable currentIssue = issueTable.get(i);

            Iterator<Map.Entry<String, Integer>> variablesIterator = currentIssue.getVariablesFreqTable().entrySet().iterator();

            while (variablesIterator.hasNext()) {
                Map.Entry<String, Integer> currentVariable = variablesIterator.next();

                if (highestOpponentVariable.getValue() <= currentVariable.getValue()) {
                    highestOpponentVariable = currentVariable;
                    highestIssueName = currentIssue.getIssueName();
                }
            }
        }

        return new String[]{highestIssueName, highestOpponentVariable.getKey()};
    }

    /**
     * Creates a bid using Bidding Strategy Three.
     *
     * @return a bid for algorithm three
     */
    public Bid getBidThirdAlgorithm(Bid lastOffer, List<IssueTable> issueTable) {

        String[] bestIssuePair = getMostWantedOpponentIssue(issueTable);

        // Creating new Bid from this point onwards

        // Putting in the best issue/variable for other agent into our bid.
        HashMap<Integer, Value> newOffer = lastOffer.getValues();

        Bid newGeneratedOffer;

        // Try's 500 times to get a random bid above the agent utility
        for (int j = 0; j < 500; j++) {

            // Creates a random bid but including the set issue variable for the other agent
            for (int i = 0; i < lastOffer.getIssues().size(); i++) {
                Issue issue = lastOffer.getIssues().get(i);
                if (!issue.getName().equals(bestIssuePair[0])) {
                    ValueDiscrete valueDiscrete = getRandomisedIssueVariable(issue);
                    newOffer.put(issue.getNumber(), valueDiscrete);
                } else {
                    IssueDiscrete issueDiscrete = (IssueDiscrete) issue;

                    // Get the ValueDiscrete of opponent most wanted.
                    for (int k = 0; k < issueDiscrete.getValues().size(); k++) {
                        ValueDiscrete valueDiscrete = issueDiscrete.getValue(k);
                        if (valueDiscrete.getValue().equals(bestIssuePair[1])) {
                            newOffer.put(issue.getNumber(), valueDiscrete);
                        }

                    }
                }
            }

            // Tests the random bid so that its greater than our utility
            newGeneratedOffer = new Bid(domain, newOffer);
            if (utilitySpace.getUtility(newGeneratedOffer) >= (agentUtility - SLACK)) {
                return newGeneratedOffer;
            }
        }

        // If NULL is returned algorithm 1 is executed.
        return null;
    }


    /**
     * When algorithm 3 fails this is the last option.
     */
    public Bid getBackUpBid(List<Issue> issues, Bid bestBid, AdditiveUtilitySpace additiveUtilitySpace) {
        LinkedHashMap<Issue, Double> issueWeights = getAgentWeights(true, issues, additiveUtilitySpace);


        // Number of random issues that will be done within 1 bid
        // this is the total issue size / 2.
        int numberRandomisedIssue = bestBid.getIssues().size();

        Set<Issue> randomSelectedIssues = new LinkedHashSet<>();

        for (int i = 0; i < 5000; i++) {

            // Local copy of issues list
            LinkedHashMap<Issue, Double> copyIssueWeights = new LinkedHashMap<>();
            for (Issue newKey : issueWeights.keySet()) {
                copyIssueWeights.put(newKey, issueWeights.get(newKey));
            }

            // Gets random amount of issues that are unique
            for (int j = 0; j < numberRandomisedIssue; j++) {
                Issue rand = getRandomIssue(copyIssueWeights);
                randomSelectedIssues.add(rand);
                copyIssueWeights.remove(rand);
            }

            // Give a random variable for the selected issue within 1 offer.
            HashMap<Integer, Value> newOffer = bestBid.getValues();
            Iterator<Issue> it = randomSelectedIssues.iterator();

            while (it.hasNext()) {
                Issue currentIssue = it.next();
                newOffer.put(currentIssue.getNumber(), getRandomisedIssueVariable(currentIssue));
            }

            Bid newBid = new Bid(domain, newOffer);

            if (utilitySpace.getUtility(newBid) >= (agentUtility - SLACK)) {
                return newBid;
            }
        }
        Log.i(TAG, "BackUp Method Failed! -> Returning Best Bid");
        return bestBid;
    }
}
