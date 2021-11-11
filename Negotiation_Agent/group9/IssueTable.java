package group9;

import genius.core.issue.IssueDiscrete;
import genius.core.issue.ValueDiscrete;

import java.util.HashMap;
import java.util.LinkedHashMap;

/**
 * Models a frequency table of issue variables in an arbitrary domain.
 * Encapsulates a {@code HashMap} which contains {@code <Variable, Frequency>} pair.
 *
 * @author: STUDENT_NAME, Pouria Toopchi, STUDENT_NAME, STUDENT_NAME (for privacy reasons names of other students were removed)
 */
public class IssueTable {

    public static HashMap<String, Integer> initFromVars(IssueDiscrete issueDiscrete) {
        int initFreqVal = 0; // all freqs. are set to 0 initially.
        HashMap<String, Integer> freqMap = new LinkedHashMap<>();
        for (ValueDiscrete value : issueDiscrete.getValues()) {
            freqMap.put(value.getValue(), initFreqVal);
        }
        return freqMap;
    }

    private String issueName;
    private HashMap<String, Integer> variablesFreqTable;

    public IssueTable(String issueName, HashMap<String, Integer> options) {
        this.issueName = issueName;
        this.variablesFreqTable = options;
    }

    /**
     * Returns the issue name.
     */
    public String getIssueName() {
        return issueName;
    }

    /**
     * @return map with the list of variables and its co-responding frequencies.
     */
    public HashMap<String, Integer> getVariablesFreqTable() {
        return variablesFreqTable;
    }
}
