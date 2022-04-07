

    library(wordcloud2)
    library(tidytext);
    library(dplyr);
            
    assertthat::assert_that(file.exists("./speeches/data/data.csv"));
    data <- read.csv("./speeches/data/data.csv",encoding = "UTF-8");
    speech_words <- data %>% 
        select(text) %>% 
        unnest_tokens(word, text);
    words <- speech_words %>% 
        count(word, sort=TRUE) %>% 
        anti_join(stop_words);
    set.seed(1234);
    wordcloud2(words, size = 0.7)

    
    
    

