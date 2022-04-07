#
# Skrypt rysuje wykres na podstawie danych z google trends
#
# Dane umieszczone są w folderze 'data'
# Można dowolnie dodawać i usuwać pliki .csv z tego folderu
#
# w google trends ustawiamy opcję "cały świat"
# od 1 stycznia 2018 roku

library(tidyverse)
library(dplyr)

## Czytamy dane

# Folder z danymi
dir_name <- file.path("google_trends", "data")

csv_files <- list.files(dir_name)

dane_przemowien <- readr::read_csv(file.path("speeches","data","data.csv"))

read_csv_file <- function(file_name) {
  readr::read_csv(file.path(dir_name, file_name), skip = 2)
}

# wektor wczytanych ramek danych
df_vector <- lapply(csv_files, read_csv_file)

# łączymy w jedną
df <- bind_cols(df_vector, .name_repair = "minimal")

# wybieramy kolumny poza zduplikowanymi kolumnami "Tydzień"
df <- df %>%
  select(-seq(3,ncol(df),2))

# zamiana wartości "<1" na 0
replace_chars_with_double <- function(column) {
  if (is.character(column)) {
    column <- replace(column, column == "<1", "0")
    return(as.double(column))
  } else {
    return(column)
  }
}

df <- df %>%
  mutate(across(!Tydzień, replace_chars_with_double))

# czyścimy nazwy
df <- df %>%
  rename_with(function(names) {
    sapply(str_split(names, ":"), function(a) a[[1]])
  })

## Wykres

df <- df %>% pivot_longer(-Tydzień, names_to = "Trend")
# nie testowane jeszcze zmienione kolory
ggplot(df, aes(x = Tydzień, y = value)) +
  geom_line(aes(color = Trend)) +
  scale_x_date(
    breaks = dane_przemowien$date,
    labels = dane_przemowien$name,
    guide = guide_axis(n=2),
    limits = c(as.Date("2018-09-01"),as.Date("2020-03-01"))
  )+
  scale_color_manual(name = "Trend",
    values = c(
      "Greta Thunberg" = "#FF0000",
       "emissions" = "#2274A5",
       "Klimat" = "#F1C40F",
       "Ślad węglowy" = "#00CC66",
       "Wylesianie" = "#613F75",
       "Zmiana klimatu" = "#C2AFF0")
      ) +
  labs(
    title = "Porównanie wyszukiwań zestawu haseł w wyszukiwarce Google",
    y = "% maksymalnej wartości trendu",
    x = "Data"
  )+
  theme(
    axis.text.x = (element_text(angle = -90))
  )

ggsave("google_trends/google_trends.png", limitsize = FALSE)

