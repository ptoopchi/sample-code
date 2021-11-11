package group9;

import genius.core.AgentID;
import genius.core.Bid;
import genius.core.Domain;
import genius.core.actions.Accept;
import genius.core.actions.Action;
import genius.core.actions.Offer;
import genius.core.issue.Issue;
import genius.core.issue.IssueDiscrete;
import genius.core.parties.AbstractNegotiationParty;
import genius.core.parties.NegotiationInfo;
import genius.core.uncertainty.BidRanking;
import genius.core.utility.AdditiveUtilitySpace;

import java.io.FileDescriptor;
import java.io.FileOutputStream;
import java.io.PrintStream;
import java.util.*;
import java.util.concurrent.TimeUnit;

/**
 * Bilaterial negotiation agent for GENIUS from Team 9.
 *
 * @author: STUDENT_NAME, Pouria Toopchi, STUDENT_NAME, STUDENT_NAME (for privacy reasons names of other students were removed)
 */
public class Agent9 extends AbstractNegotiationParty {

    // Convenience parameter for quickly toggling frequency table printout.
    private final static boolean IS_PRINT_FREQ_TABLE = false;

    // Used by logger.
    final static Class TAG = Agent9.class;

    // Used to measure agent run time.
    private long startTime;
    private long endTime;

    /**
     * Linear uitlity for first 2 rounds.
     */
    private int roundCounter = 2;

    private int prefElicitRoundCounter = 1;

    /**
     * Agent's target utility is based on hyperparameter (β) and time elapsed (t).
     * Time is 0.0 at the start of the negotiation.
     * 
     * Note: The target utility starts from a high value and decreases as
     * time passes.
     *
     */
    private double agentTargetUtility = setTargetUtility();

    /**
     * Stores the last last offer from the opponent.
     */
    private Bid opponentPreviousOffer = null;

    /**
     * Table storing the issues and variables.
     */
    private final ArrayList<IssueTable> issuesList = new ArrayList<>();

    /**
     * Contains the last bid received from the opponent.
     */
    private Bid lastOffer;

    /**
     * The domain of the negotiation.
     */
    private Domain domain;

    /**
     * List of issues in this domain.
     */
    private List<Issue> issues;

    /**
     * Gives the best bid in the domain space.
     */
    private Bid bestBid;
    private PreferenceElicitation pElicitate;


    private ArrayList<Double> previousOpponentOfferUtility = new ArrayList<>();

    /**
     * Initializes a new instance of the agent.
     */
    @Override
    public void init(NegotiationInfo info) {
        super.init(info);
        startTime = System.nanoTime();

        /*
         * Terminology conventions:
         *     - issues are called issues
         *     - values in issues are called variables
         */
        domain = getDomain();

        /*
         * Returns a list of issues within this negotiation.
         * Note: All Issues in the domain, sorted to preorder. This may be computationally expensive)
         */
        issues = domain.getIssues();

        System.setOut(new PrintStream(new FileOutputStream(FileDescriptor.out)));
        if (this.hasPreferenceUncertainty()) {
            try {
                BidRanking bidRanking = this.userModel.getBidRanking();
                pElicitate = new PreferenceElicitation(domain, info);
                pElicitate.estimateUncertainty(bidRanking);
                bestBid = getUtilitySpace().getMaxUtilityBid();
            } catch (Exception e) {
                Log.e(TAG, "Preference elicitation failed!");
                e.printStackTrace();
            }
        } else {
            try {
                bestBid = getUtilitySpace().getMaxUtilityBid();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }

        for (int i = 0; i < issues.size(); i++) {
            Issue issue = issues.get(i);
            // This agent is only compatible with discrete issues.
            IssueDiscrete issueDiscrete = (IssueDiscrete) issue;

            // Creates a new Issue instance
            issuesList.add(
                    new IssueTable(issue.getName(), IssueTable.initFromVars(issueDiscrete)));
            double weight = ((AdditiveUtilitySpace) utilitySpace).getWeight(issue.getNumber());
            String name = issue.getName();
            Log.a(TAG, "Issue name, weight: {" + name + ", " + weight + "}");
        }
        Log.d(TAG, "Agent initialised.");
//        printIssuesTable();
    }

    /**
     * Selects Agent Algorithm
     *
     * @return our agent offer
     */
    @Override
    public Action chooseAction(List<Class<? extends Action>> possibleActions) {

        Log.d(TAG, "------------------------");
        BiddingStrategy biddingStrategy = new BiddingStrategy(agentTargetUtility, utilitySpace, domain);
        Log.d(TAG, "Agent's target utility is: " + agentTargetUtility);
        Log.e(TAG, " OPPONENT OFFER " + lastOffer);
        /*
         * Applies only for first move.
         * Apply "Algorithm 1" from Pars Agent.
         */
        if (lastOffer == null) {
            try {
                Bid offer = biddingStrategy.getBidFirstAlgorithm(issues, bestBid, ((AdditiveUtilitySpace) utilitySpace));
                Log.i(TAG, "Algorithm 1 is choosing to make a bid with utility: " +
                        utilitySpace.getUtility(offer));
                Log.d(TAG, "This contains: " + offer.toString());
                return new Offer(getPartyId(), offer);
            } catch (Exception e) {
                Log.e(TAG, "Agent could not obtain max utility bid!" + ", " + e.getMessage());
            }
        }
        /*
         * Applies for every move, except first move (see above).
         * May apply Pars agent "Algorithm 2" or "Algorithm 3".
         */
        else {
            Log.d(TAG, "Opponent made an offer with utility: " + utilitySpace.getUtility(lastOffer));
            try {
                if (roundCounter == 1) {
                    Bid offer = biddingStrategy.getBidFirstAlgorithm(issues, bestBid, ((AdditiveUtilitySpace) utilitySpace));
                    opponentPreviousOffer = lastOffer;
                    agentTargetUtility = setTargetUtility();
                    return new Offer(getPartyId(), offer);
                }

                // elictRank
                if (prefElicitRoundCounter < 25) {
                    List<Bid> bidOrder = userModel.getBidRanking().getBidOrder();
                    if (!bidOrder.contains(lastOffer) && !isNullLastOffer(lastOffer)) {
                        userModel = user.elicitRank(lastOffer, userModel);
                        BidRanking bidRanking = this.userModel.getBidRanking();
                        pElicitate.estimateUncertainty(bidRanking);
                        prefElicitRoundCounter++;
                    }
                }

                if ((getUtility(lastOffer) >= agentTargetUtility - 0.03
                        && getUtility(lastOffer) >= utilitySpace.getReservationValue()) ||
                        (timeline.getTime() >= 0.99 && getUtility(lastOffer) >= utilitySpace.getReservationValue())) {
                    Log.i(TAG, "Agent will accept offer with utility: " + utilitySpace.getUtility(lastOffer));
                    Log.d(TAG, "Agent's target utility was: " + agentTargetUtility);
                    return new Accept(getPartyId(), lastOffer);
                }

                // Update the agents utility depending on time.
                // Note: Change this later.
                agentTargetUtility = setTargetUtility();

                // Refresh frequency table with information from last offer.
                updateTable(lastOffer);

                // Agent second move offer
                Bid offer = biddingStrategy.getBidSecondAlgorithm(issues, lastOffer,
                        ((AdditiveUtilitySpace) utilitySpace));
                // When offer is null this is part 3
                // When not null a randomised offer is returned to the other agent
                // Based on the lastOffer sent to us
                if (offer == null) {

                    Log.w(TAG, "Algorithm 2 failed, attempting Algorithm 3");

                    offer = biddingStrategy.getBidThirdAlgorithm(lastOffer, issuesList);

                    if (offer == null) {
                        Log.w(TAG, "Algorithm 3 failed, attempting updated Algorithm 1");
                        offer = biddingStrategy.getBackUpBid(issues, bestBid, ((AdditiveUtilitySpace) utilitySpace));
                        Log.i(TAG, "Backup algorithm is choosing to make a bid with utility: " +
                                utilitySpace.getUtility(offer));
                    }

                    Log.i(TAG, "Algorithm 3 is choosing to make a bid with utility: " +
                            utilitySpace.getUtility(offer));
                    Log.d(TAG, "This contains: " + offer.toString());
                    opponentPreviousOffer = lastOffer;
                    return new Offer(getPartyId(), offer);
                } else {
                    opponentPreviousOffer = lastOffer;
                    return new Offer(getPartyId(), offer);
                }
            } catch (Exception e) {
                Log.e(TAG, "Failed to get max utility when the other agent gave an offer");
                e.printStackTrace();
            }


            opponentPreviousOffer = lastOffer;
            // Updates the Frequency Table
            if (timeline.getTime() >= 0.99 && utilitySpace.getUtility(lastOffer) >= utilitySpace.getReservationValue()) {
                Log.w(TAG, "Time up, ending negotiation!");
                return new Accept(getPartyId(), lastOffer);
            }
        }

        // This should never happen but incase of error it sends out a random offer above the target utility
        Bid randomBidAboveTarget = generateRandomBidAboveTarget();
        Log.w(TAG, "All algorithms failed. Sending random offer: " + randomBidAboveTarget);
        opponentPreviousOffer = lastOffer;
        return new Offer(getPartyId(), randomBidAboveTarget);
    }

    public Boolean isNullLastOffer(Bid lastOffer) {
        return domain.getIssues().size() < lastOffer.getIssues().size();
    }

    /**
     * Generates Random Bid above target utility.
     *
     * @return random bid
     */
    private Bid generateRandomBidAboveTarget() {
        Bid randomBid;
        double util;
        int i = 0;
        // try 100 times to find a bid under the target utility

        do {
            randomBid = generateRandomBid();
            util = utilitySpace.getUtility(randomBid);
            i++;
        }
        while (util < agentTargetUtility && i < 100);
        return randomBid;
    }

    /**
     * Updates the table of the opponents offers.
     * This will increase the frequency of each issue/domain
     * the more the opponent brings it up during negotiation
     */
    private void updateTable(Bid lastOffer) {

        // Loop through the last offer issues
        for (int i = 0; i < lastOffer.getIssues().size(); i++) {

            // Get the offer name and the value selected for that last offer
            String offerName = lastOffer.getIssues().get(i).getName();
            String offerValue = lastOffer.getValue(lastOffer.getIssues().get(i).getNumber()).toString();

            // Go through the list of issues and update the Hash map for the frequencies
            for (int j = 0; j < issuesList.size(); j++) {
                IssueTable issue = issuesList.get(j);

                if (issue.getIssueName().equals(offerName)) {
                    issue.getVariablesFreqTable().put(offerValue, issue.getVariablesFreqTable().get(offerValue) + 1);
                }
            }
        }
    }

    /**
     * (To check all domains + Issues are printed correctly)
     * Print of all the issues and the domains
     */
    private void printIssuesTable() {
        StringBuilder sb = new StringBuilder();

        for (int j = 0; j < issuesList.size(); j++) {
            IssueTable issue = issuesList.get(j);
            sb.append("Domain Name: ").append(issue.getIssueName()).append(" \n");
            sb.append("     Domain Values: ");
            issue.getVariablesFreqTable().forEach((key, value) -> sb.append("{")
                    .append(key).append(",").append(value).append("} "));
            sb.append("\n");
        }

        System.out.println(sb.toString());
    }

    /**
     * Prints frequency table for issues in this domain.
     *
     * @param issueTable
     */
    private void printTable(List<IssueTable> issueTable) {
        if (issueTable.size() > 25) {
            Log.e(TAG, "Request to log table denied due to large number of issues.");
        }
        System.out.println("------------------------");
        for (int i = 0; i < issueTable.size(); i++) {
            IssueTable issueRow = issueTable.get(i);
            String issueName = issueRow.getIssueName();
            System.out.println("Issue " + (i + 1) + ": \"" + issueName + "\"");
            HashMap<String, Integer> variableFrequencyMap = issueRow.getVariablesFreqTable();
            for (Map.Entry<String, Integer> entry : variableFrequencyMap.entrySet()) {
                System.out.print("    {\"" + entry.getKey() + "\", " + entry.getValue() + "} ");
            }
            System.out.print("\n");
        }
        System.out.println("------------------------");
    }

    /**
     * Sets and updates the target utility using tit for tat.
     */
    private double setTargetUtility() {
        if (roundCounter > 0) {
            roundCounter--;
            return 1.0;
        }

        double opponentConcession = (utilitySpace.getUtility(lastOffer) - utilitySpace.getUtility(opponentPreviousOffer));

        if (opponentConcession <= 0.0) {
            if (opponentConcession == 0.0) previousOpponentOfferUtility.add(utilitySpace.getUtility(lastOffer));

            Log.d(TAG, "Negative concession");
            return agentTargetUtility;
        }

        // ( ( 2 * arctan(15x - 5) / 8pi) + 0.109 ) where x is the opponent concession
        double agentConcession = ((2 * Math.atan(15 * opponentConcession - 5)) / (8 * Math.PI)) + 0.109;
        agentConcession *= 0.5;
        agentConcession = Math.abs(agentConcession);

        Log.d(TAG, "Round opponentConcession: " + opponentConcession);
        Log.d(TAG, "Round agentConcession: " + agentConcession);


        int sizeOfArray = previousOpponentOfferUtility.size();

        if (previousOpponentOfferUtility.size() >= 3) {

            boolean check = (previousOpponentOfferUtility.get(sizeOfArray - 1)
                    .equals(previousOpponentOfferUtility.get(sizeOfArray - 2))) &&
                    (previousOpponentOfferUtility.get(sizeOfArray - 2)
                            .equals(previousOpponentOfferUtility.get(sizeOfArray - 3)));

            if (check) {
                if (agentTargetUtility - agentConcession < 0.68) {
                    return 0.68;
                } else {
                    return agentTargetUtility - 0.05;
                }
            }
        }

        if (agentTargetUtility - agentConcession < 0.68) {
            return 0.68;
        }

        return agentTargetUtility - agentConcession;
    }

    /**
     * Remembers the offers received by the opponent.
     */
    @Override
    public void receiveMessage(AgentID sender, Action action) {
        if (action instanceof Offer) {
            lastOffer = ((Offer) action).getBid();
        }
    }

    /**
     * Method is used to print the issues table before the thread of agent is killed.
     *
     * @return super class of negotiation end.
     */
    @Override
    public HashMap<String, String> negotiationEnded(Bid acceptedBid) {
        Log.d(TAG, "------------------------");
        if (IS_PRINT_FREQ_TABLE) {
            Log.d(TAG, "Frequency table after final round:");
            printTable(issuesList);
        }

        Log.a(TAG, "Issue weights after final round:");
        for (int i = 0; i < issues.size(); i++) {
            Issue issue = issues.get(i);
            double weight = ((AdditiveUtilitySpace) utilitySpace).getWeight(issue.getNumber());
            String name = issue.getName();
            Log.a(TAG, "Issue name, weight: {" + name + ", " + weight + "}");
        }

        Log.d(TAG, "Negotiation ended.");
        Log.i(TAG, "No. of negotiation issues in this domain: " + issuesList.size());
        endTime = System.nanoTime();
        long totalTimeNanoSecs = endTime - startTime;
        long totalTimeMilliSecs = TimeUnit.NANOSECONDS.toMillis(totalTimeNanoSecs);
        Log.i(TAG, "Total runtime for agent: " + totalTimeMilliSecs + " ms");
        return super.negotiationEnded(acceptedBid);
    }
}
