package project.gui.viewcontrollers;

import javafx.fxml.FXML;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import javafx.scene.control.TextFormatter;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import javafx.util.converter.DoubleStringConverter;
import project.dataholder.DataHolder;
import project.dataholder.UserInput;
import project.dataprocessing.Rate;
import project.dataprocessing.RateCollection;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.function.UnaryOperator;

public class CalculatorViewController extends ViewController {

    @FXML
    private HBox calculatorBox;

    @FXML
    private Label calculatorTitle;

    private static class CalculatorField {
        public final String currencyCode;
        public final Rate lastRate;
        public final TextField field;

        public CalculatorField(String currencyCode, Rate lastRate, TextField field) {
            this.currencyCode = currencyCode;
            this.lastRate = lastRate;
            this.field = field;
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;
            CalculatorField that = (CalculatorField) o;
            return currencyCode.equals(that.currencyCode);
        }
    }

    private final List<CalculatorField> calculatorFields = new ArrayList<>();

    @Override
    public void updateView() {
        updateTitle(DataHolder.getUserInput());
        createCalculator(DataHolder.getRates());
    }

    private void updateTitle(UserInput userInput) {
        calculatorTitle.setText("Kurs z dnia " + userInput.endDate.toString());
    }

    private void createCalculator(Map<String, RateCollection> rates) {
        clearCalculatorBox();
        createCalculatorFieldList(rates);
        createLabelAndFieldBoxes();
        setEventHandlersOnFields();
        setDefaultValues();
    }

    private void clearCalculatorBox() {
        calculatorBox.getChildren().clear();
    }

    private void createCalculatorFieldList(Map<String, RateCollection> rates) {
        calculatorFields.clear();
        addPlnCalculatorField();
        for (Map.Entry<String, RateCollection> currency : rates.entrySet()) {
            addCalculatorField(currency.getKey(), currency.getValue());
        }
    }

    private void addPlnCalculatorField() {
        Rate plnRate = new Rate("PLN", LocalDate.now().minusDays(1), 1.00);
        RateCollection plnRateCollection = new RateCollection(List.of(plnRate));
        addCalculatorField("PLN", plnRateCollection);
    }

    private void addCalculatorField(String currencyCode, RateCollection rateCollection) {
        Rate lastRate = getLastRate(rateCollection);
        TextField field = new TextField();
        calculatorFields.add(new CalculatorField(currencyCode, lastRate, field));
    }

    private Rate getLastRate(RateCollection rateCollection) {
        return rateCollection.items.get(rateCollection.items.size() - 1);
    }

    private void createLabelAndFieldBoxes() {
        for (CalculatorField calculatorField : calculatorFields) {
            Label label = new Label(calculatorField.currencyCode);
            VBox labelAndFieldBox = new VBox(label, calculatorField.field);
            calculatorBox.getChildren().add(labelAndFieldBox);
        }
    }

    private void setEventHandlersOnFields() {
        for (CalculatorField calculatorField : calculatorFields) {

            UnaryOperator<TextFormatter.Change> doubleFilter = change -> {
                String newValue = change.getControlNewText();
                if (newValue.matches("\\d*|\\d+\\.\\d*")) {
                    return change;
                }
                return null;
            };

            calculatorField.field.setOnKeyTyped(keyEvent -> updateAllFieldsValues(calculatorField));

            calculatorField.field.setTextFormatter(
                    new TextFormatter<>(new DoubleStringConverter(), null, doubleFilter));
        }
    }

    private void updateAllFieldsValues(CalculatorField changedCalculatorField) {
        for (CalculatorField calculatorField : calculatorFields) {
            updateFieldValue(calculatorField, changedCalculatorField);
        }
    }

    private void updateFieldValue(CalculatorField calculatorField, CalculatorField changedCalculatorField) {
        if (calculatorField.equals(changedCalculatorField)) {
            return;
        }
        if (changedCalculatorField.field.getText().isEmpty()) {
            return;
        }
        double amountOfMoney = Double.parseDouble(changedCalculatorField.field.getText());
        double newAmountOfMoney = changedCalculatorField.lastRate.getValue() * amountOfMoney / calculatorField.lastRate.getValue();
        calculatorField.field.setText(String.format(Locale.US, "%.2f", newAmountOfMoney));
    }

    private void setDefaultValues() {
        if (!calculatorFields.isEmpty()) {
            CalculatorField firstCalculatorField = calculatorFields.get(0);
            firstCalculatorField.field.setText("100.0");
            updateAllFieldsValues(firstCalculatorField);
        }
    }
}
