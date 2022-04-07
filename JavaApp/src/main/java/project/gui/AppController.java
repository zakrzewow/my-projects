package project.gui;


import javafx.embed.swing.SwingFXUtils;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.fxml.Initializable;
import javafx.scene.Parent;
import javafx.scene.control.*;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.VBox;
import javafx.stage.FileChooser;
import project.App;
import project.dataholder.DataHolder;
import project.dataholder.UserInput;
import project.dataprocessing.NbpParser;
import project.dataprocessing.RateCollection;
import project.gui.viewcontrollers.ViewController;

import javax.imageio.ImageIO;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.net.URL;
import java.time.LocalDate;
import java.util.*;
import java.util.stream.Collectors;

public class AppController implements Initializable {

    private static class View {
        public ViewController controller;
        public Parent parent;

        public View(ViewController controller, Parent parent) {
            this.controller = controller;
            this.parent = parent;
        }
    }

    private final Map<String, View> viewMap = new HashMap<>();
    private View currentView = null;

    @FXML
    private BorderPane mainPane;

    @FXML
    private DatePicker startDatePicker;

    @FXML
    private DatePicker endDatePicker;

    @FXML
    private Label dateRangeSelectLabel;

    @FXML
    private Label singleDateSelectLabel;

    @FXML
    public VBox checkBoxesPane;

    List<CheckBox> checkBoxes = new ArrayList<>();

    private void loadView(String viewName) {
        try {
            URL url = App.class.getResource("/views/" + viewName + ".fxml");
            FXMLLoader loader = new FXMLLoader(url);
            Parent parent = loader.load();
            ViewController controller = loader.getController();
            viewMap.put(viewName, new View(controller, parent));
        } catch (IOException e) {
            System.out.println("Cannot find view with specific name: " + viewName);
            e.printStackTrace();
        }
    }

    public AppController() {
        loadView("chartView");
        loadView("trendsView");
        loadView("calculatorView");
    }

    @Override
    public void initialize(URL url, ResourceBundle resourceBundle) {
        setCenterView("chartView");
        initializeCheckBoxes();
        initializeDateRangeSelecting();
        setDefaultValues();
    }

    private void setCenterView(String viewName) {
        currentView = viewMap.get(viewName);
        mainPane.setCenter(currentView.parent);
        if (!DataHolder.isEmpty()) {
            currentView.controller.updateView();
        }
    }

    private void initializeCheckBoxes() {
        for (String code : List.of("Gold", "USD", "GBP", "EUR", "JPY", "CHF")) {
            checkBoxes.add(new CheckBox(code));
        }
        checkBoxesPane.getChildren().addAll(checkBoxes);
    }

    private void setDefaultValues() {
        checkBoxes.stream().skip(1).forEach(c -> c.setSelected(true));
        LocalDate localDate = LocalDate.now();
        startDatePicker.setValue(localDate.minusMonths(6));
        endDatePicker.setValue(localDate.minusDays(1));
    }

    private void initializeDateRangeSelecting() {
        singleDateSelectLabel.setVisible(false);
        singleDateSelectLabel.setManaged(false);
        dateRangeSelectLabel.setVisible(true);
        dateRangeSelectLabel.setManaged(true);
        startDatePicker.setVisible(true);
        startDatePicker.setManaged(true);
    }

    private void initializeSingleDateSelecting() {
        dateRangeSelectLabel.setVisible(false);
        dateRangeSelectLabel.setManaged(false);
        singleDateSelectLabel.setVisible(true);
        singleDateSelectLabel.setManaged(true);
        startDatePicker.setVisible(false);
        startDatePicker.setManaged(false);
    }

    @FXML
    private void handleShowChartView() {
        setCenterView("chartView");
        initializeDateRangeSelecting();
    }

    @FXML
    private void handleShowCalculatorView() {
        setCenterView("calculatorView");
        initializeSingleDateSelecting();
    }

    @FXML
    private void handleShowTrendsView() {
        setCenterView("trendsView");
        initializeDateRangeSelecting();
    }

    @FXML
    private void handleConfirmInput() {
        UserInput userInput = collectUserInput();
        DataHolder.fetchRatesFromServer(userInput);
        currentView.controller.updateView();
    }

    private UserInput collectUserInput() {
        return new UserInput(
                startDatePicker.getValue(),
                endDatePicker.getValue(),
                collectCheckBoxesInput()
        );
    }

    private List<String> collectCheckBoxesInput() {
        return checkBoxes.stream()
                .filter(CheckBox::isSelected)
                .map(checkBox -> checkBox.textProperty().get())
                .collect(Collectors.toList());
    }

    private File getFileFromFileChooser(String format) {
        FileChooser fileChooser = new FileChooser();
        FileChooser.ExtensionFilter extFilter = new FileChooser.ExtensionFilter(
                format.toUpperCase() + " files (*." + format.toLowerCase() + ")", "*." + format.toLowerCase());
        fileChooser.getExtensionFilters().add(extFilter);
        return fileChooser.showSaveDialog(null);
    }

    @FXML
    private void saveCsv() {
        saveToFile("csv");
    }

    @FXML
    private void saveJson() {
        saveToFile("json");
    }

    private void saveToFile(String format) {

        List<String> selectedCodes = collectCheckBoxesInput();

        if(selectedCodes.size() == 0) {
            currencyNotCheckedAlert();
            return;
        }

        File file = getFileFromFileChooser(format);
        LocalDate startDate = startDatePicker.getValue();
        LocalDate endDate = endDatePicker.getValue();

        RateCollection rateCollection = NbpParser.getRateCollectionByCodes(selectedCodes, startDate, endDate);
        rateCollection.sortByDate();

        try {
            BufferedWriter writer = new BufferedWriter(new FileWriter(file));
            writer.write( rateCollection.toFormat(format) );
            writer.close();
        } catch (IOException e) {
            e.printStackTrace();
        }

    }

    private void currencyNotCheckedAlert() {
        Alert alert = new Alert(Alert.AlertType.ERROR);
        alert.setContentText("Nie wybrano waluty.");
        alert.show();
    }
}