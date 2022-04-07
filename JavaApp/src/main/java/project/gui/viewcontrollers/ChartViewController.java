package project.gui.viewcontrollers;

import javafx.embed.swing.SwingFXUtils;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.scene.chart.LineChart;
import javafx.scene.chart.XYChart;
import javafx.scene.image.WritableImage;
import javafx.stage.FileChooser;
import project.dataholder.DataHolder;
import project.dataprocessing.RateCollection;

import javax.imageio.ImageIO;
import java.io.File;
import java.io.IOException;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;

public class ChartViewController extends ViewController {
    @FXML
    private LineChart<String, Double> lineChart;

    @Override
    public void updateView() {
        clearChart();

        Map<String, RateCollection> rates = DataHolder.getRates();
        updateChart(rates);
    }

    private void clearChart() {
        lineChart.getData().clear();
    }

    private void updateChart(Map<String, RateCollection> rates) {
        for (String currencyCode: rates.keySet()) {

            RateCollection rate = rates.get(currencyCode);
            List<Double> values = rate.getValues();
            List<LocalDate> dates = rate.getDates();

            XYChart.Series<String, Double> series = new XYChart.Series<>();
            series.setName(currencyCode);
            for (int i = 0; i < values.size(); i++) {
                series.getData().add(new XYChart.Data<>(dates.get(i).toString(), values.get(i)));
            }
            lineChart.getData().add(series);
        }
    }

    @FXML
    private void handleSave() {
        File file = getFileFromFileChooser();
        try {
            ImageIO.write(SwingFXUtils.fromFXImage(getImage(), null),
                    "png", file);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private File getFileFromFileChooser() {
        FileChooser fileChooser = new FileChooser();
        FileChooser.ExtensionFilter extFilter = new FileChooser.ExtensionFilter(
                "PNG files (*.png)", "*.png");
        fileChooser.getExtensionFilters().add(extFilter);

        return fileChooser.showSaveDialog(null);
    }

    private WritableImage getImage() {
        return lineChart.snapshot(null, null);
    }
}
