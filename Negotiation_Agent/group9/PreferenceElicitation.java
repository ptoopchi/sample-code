package group9;

import genius.core.Bid;
import genius.core.Domain;
import genius.core.issue.Issue;
import genius.core.issue.ValueDiscrete;
import genius.core.parties.NegotiationInfo;
import genius.core.uncertainty.BidRanking;
import genius.core.utility.AbstractUtilitySpace;
import genius.core.utility.AdditiveUtilitySpace;
import genius.core.utility.EvaluatorDiscrete;
import gurobi.*;

import java.util.*;

/**
 * Uses Linear Programming to estimate issue weights.
 */
public class PreferenceElicitation {

    private final Domain domain;
    public NegotiationInfo info;

    public PreferenceElicitation(Domain domain, NegotiationInfo negotiationInfo) {
        this.domain = domain;
        this.info = negotiationInfo;
    }

    public void estimateUncertainty(BidRanking rankedBids) throws Exception {
        AbstractUtilitySpace utilitySpace = this.info.getUtilitySpace();
        AdditiveUtilitySpace additiveUtilitySpace = (AdditiveUtilitySpace) utilitySpace;

        List<Bid> rankedBidsList = rankedBids.getBidOrder();
        List<Issue> issues = this.domain.getIssues();

        int totalNumberOfSlackVariables = rankedBidsList.size() - 1;

        GRBEnv env = new GRBEnv();
        env.set("OutputFlag", "0"); // Remove Output from gurobi
        GRBModel model = new GRBModel(env);
        model.set(GRB.StringAttr.ModelName, "optimal-agent");

        // Making slack variables (z)
        List<GRBVar> slackVariables = new ArrayList<>(totalNumberOfSlackVariables);
        for (int i = 0; i < totalNumberOfSlackVariables; i++) {
            slackVariables.add(model.addVar(0, GRB.INFINITY, 0, GRB.CONTINUOUS, "z[" + i + "]"));
        }

        // Define objective fn.
        // Eqn: 14, Tsimpoukis 2019
        GRBLinExpr objLinExpr = new GRBLinExpr();
        for (int i = 0; i < slackVariables.size(); i++) {
            objLinExpr.addTerm(1d, slackVariables.get(i));
        }
        model.setObjective(objLinExpr, GRB.MINIMIZE);

        // Non-negativity constraints for slack variables
        // Eqn: 16, Tsimpoukis 2019
        for (int i = 0; i < slackVariables.size(); i++) {
            GRBLinExpr slackNnExpr = new GRBLinExpr();
            slackNnExpr.addTerm(1, slackVariables.get(i));
            model.addConstr(slackNnExpr, GRB.GREATER_EQUAL, 0, "slackVar_nn[" + i + "]");
        }

        // Making issue weight variables
        int numberOfIssues = issues.size();
        List<GRBVar> weightVariables = new ArrayList<>(numberOfIssues);
        for (int i = 0; i < numberOfIssues; i++) {
            weightVariables.add(model.addVar(0, 1, 0, GRB.CONTINUOUS, "w[" + i + "]"));
        }

        // Define sum of weight constraint
        // Eqn: 4, Tsimpoukis, 2019
        GRBLinExpr weightLinExpr = new GRBLinExpr();
        for (int i = 0; i < weightVariables.size(); i++) {
            weightLinExpr.addTerm(1, weightVariables.get(i));
        }
        model.addConstr(weightLinExpr, GRB.EQUAL, 1, "wVar_sum");

        // Making ϕ variables
        // Eqn: 17, Tsimpoukis 2019
        List<List<Double>> evalList = new ArrayList<>();
        for (int i = 0, rankedBidsListSize = rankedBidsList.size(); i < rankedBidsListSize; i++) {
            Bid rankedBid = rankedBidsList.get(i);
            List<Issue> rankedIssues = rankedBid.getIssues();
            List<Double> row = new ArrayList<>(rankedIssues.size());
            int rankedIssuesSize = rankedIssues.size();
            for (int j = 0; j < rankedIssuesSize; j++) {
                GRBLinExpr phiLinExpr = new GRBLinExpr();
                Issue rankedIssue = rankedIssues.get(j);
                int issueNumber = rankedIssue.getNumber();
                EvaluatorDiscrete evaluatorDiscrete = (EvaluatorDiscrete) additiveUtilitySpace
                        .getEvaluator(issueNumber);
                ValueDiscrete valueDiscrete = (ValueDiscrete) rankedBid.getValue(issueNumber);
                Double evaluation = evaluatorDiscrete.getEvaluation(valueDiscrete);
                phiLinExpr.addTerm(evaluation, weightVariables.get(j));
                model.addConstr(phiLinExpr, GRB.GREATER_EQUAL, 0, "phiVar_nn[" + i + "_" + j + "]");
                row.add(evaluation);
            }
            evalList.add(row);
        }

        // Making Δu variables
        // Eqn: 13, Tsimpoukis 2019
        for (int i = 0; i < evalList.size() - 1; i++) {
            GRBLinExpr deltaULinExpr = new GRBLinExpr();
            for (int j = 0; j < evalList.get(i).size(); j++) {
                double variableEval1 = evalList.get(i).get(j);
                double variableEval2 = evalList.get(i + 1).get(j);
                deltaULinExpr.addTerm(variableEval1, weightVariables.get(j));
                deltaULinExpr.addTerm(-1 * variableEval2, weightVariables.get(j));
            }
            deltaULinExpr.addTerm(1, slackVariables.get(i));
            model.addConstr(deltaULinExpr, GRB.GREATER_EQUAL, 0, "deltaU_nn[" + i + "]");
        }

        // LP optimisation
        model.optimize();

        double[] newWeights = getWeightUsingSolution(numberOfIssues, weightVariables);
        additiveUtilitySpace.setWeights(issues, newWeights);

        // Uncomment to see LP logs
        // model.write("LPlog_2.lp");
        model.dispose();
        env.dispose();
    }

    private double[] getWeightUsingSolution(int numberOfIssues, List<GRBVar> weightVariables) throws GRBException {
        double[] newWeights = new double[weightVariables.size()];
        for (int i = 0; i < numberOfIssues; i++) {
            double solutionWeight = weightVariables.get(i).get(GRB.DoubleAttr.X);
            newWeights[i] = solutionWeight;
        }
        return newWeights;
    }
}
