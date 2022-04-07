package project.gui.viewcontrollers;

import javafx.fxml.FXML;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableView;
import project.dataholder.DataHolder;
import project.dataholder.UserInput;
import project.dataprocessing.RateCollection;

import java.util.List;
import java.util.Map;

public class TrendsViewController extends ViewController {

    @FXML
    private TableView<Row> tableView;

    @FXML
    private TableColumn<Row, Double> startValueColumn;

    @FXML
    private TableColumn<Row, Double> endValueColumn;

    @Override
    public void updateView() {
        clearTable();

        UserInput userInput = DataHolder.getUserInput();
        setColumnsText(userInput);

        Map<String, RateCollection> rates = DataHolder.getRates();
        createRows(rates);
    }

    private void clearTable() {
        tableView.getItems().clear();
    }

    private void setColumnsText(UserInput userInput) {
        startValueColumn.setText(userInput.startDate.toString());
        endValueColumn.setText(userInput.endDate.toString());
    }

    private void createRows(Map<String, RateCollection> rates) {
        for (String currencyCode : rates.keySet()) {

            RateCollection rate = rates.get(currencyCode);
            List<Double> values = rate.getValues();

            double startValue = values.get(0);
            double endValue = values.get(values.size() - 1);
            double change = endValue / startValue * 100 - 100;
            String sign = change > 0 ? "+" : "";
            String changeFormatted = String.format("%s%.2f%%", sign, change);

            tableView.getItems().add(new Row(currencyCode, startValue, endValue, changeFormatted));
        }
    }

    public static class Row {
        public String currencyCode;
        public Double startValue;
        public Double endValue;
        public String change;

        public Row(String currencyCode, Double startValue, Double endValue, String change) {
            this.currencyCode = currencyCode;
            this.startValue = startValue;
            this.endValue = endValue;
            this.change = change;
        }

        public String getCurrencyCode() {
            return currencyCode;
        }

        public Double getStartValue() {
            return startValue;
        }

        public Double getEndValue() {
            return endValue;
        }

        public String getChange() {
            return change;
        }
    }

}
