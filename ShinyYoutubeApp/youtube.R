library(rjson)
library(dplyr)
library(janitor)


youtube <- fromJSON(file = "historia.json")
ramka <- data.frame(unlist(youtube1[1]))
rownames(ramka) <- names(unlist(youtube[1]))
ramka <- rownames_to_column(ramka)
for(i in 2:length(youtube)){
  a <- data.frame(unlist(youtube1[i]))
  rownames(a) <- names(unlist(youtube[i]))
  ramka <- full_join(ramka, rownames_to_column(a), by=c("rowname"))
}

ramka <- t(ramka)
ramka <- ramka %>% row_to_names(row_number = 1)
rownames(ramka) <- 1:dim(ramka)[1]
ramka <- data.frame(ramka)
ramka <- ramka %>% 
  select(-header, -products, -activityControls)
ramka$titleUrl <- sub(".*?v=", "", ramka$titleUrl)
ramka$subtitles.url <- sub(".*channel/", "", ramka$subtitles.url)
