# Przykłady z https://www.tidytextmining.com/tidytext.html
# przerobione pod przemówienia Grety

library(tidytext)
library(dplyr)
library(ggplot2)
        
assertthat::assert_that(file.exists("speeches/data/data.csv"));
data <- read.csv("speeches/data/data.csv", encoding = "UTF-8");
df <- tibble(data)

tidy_speeches <- df %>% 
  unnest_tokens(word, text) %>% 
  mutate(wordnumber = row_number()) %>%
  anti_join(stop_words)

# word frequency

tidy_speeches %>%  
  count(word, sort = TRUE) %>% 
  filter(n > 20) %>% 
  mutate(word = reorder(word, n)) %>% 
  ggplot(aes(x = n, y = word)) +
  geom_col() +
  labs(
    title = "Najczęściej używane słowa w przemówieniach",
    x = "Liczba wystąpień",
    y = "Słowo"
  ) 

ggsave("speeches/tidytext/word_frequency_all.png")

# positive / negative words

bing_word_counts <- tidy_speeches %>%
  inner_join(get_sentiments("bing")) %>%
  count(word, sentiment, sort = TRUE) %>%
  ungroup()

bing_word_counts %>%
  group_by(sentiment) %>%
  slice_max(n, n = 10) %>% 
  ungroup() %>%
  mutate(word = reorder(word, n)) %>%
  ggplot(aes(n, word, fill = sentiment)) +
  geom_col(show.legend = FALSE) +
  facet_wrap(~sentiment, scales = "free") +
  labs(
    title = "Analiza sentymentu",
    subtitle = "Najbardziej pozytywne i negatywne słowa użyte w przemówieniach",
    x = "Wkład w sentyment",
    y = NULL)


ggsave("speeches/tidytext/contribution_to_sentiment.png")


# sentiment via speeches

library(tidyr)

speeches_sentiment <- tidy_speeches %>%
  inner_join(get_sentiments("bing")) %>%
  count(name, index = wordnumber %/% 50, sentiment) %>%
  pivot_wider(names_from = sentiment, values_from = n, values_fill = 0) %>% 
  mutate(sentiment = positive - negative)

ggplot(speeches_sentiment, aes(index, sentiment, fill = name)) +
  geom_col(show.legend = FALSE) +
  labs(
    title = "Sumaryczny sentyment z każdych 50 słów na przestrzeni wszystkich przemówień",
    y = "Sentyment",
    x = "Fragment przemówienia")

ggsave("speeches/tidytext/sentiment_via_speeches.png")


# wordcloud

library(wordcloud)

tidy_speeches %>%
  count(word) %>%
  with(wordcloud(word, n, max.words = 100))

ggsave("speeches/tidytext/worldcloudv2.png")

# tf idf

speeches_words <- df %>%
  unnest_tokens(word, text) %>%
  count(name, word, sort = TRUE)

total_words <- speeches_words %>% 
  group_by(name) %>% 
  summarize(total = sum(n))

speeches_words <- left_join(speeches_words, total_words)

speech_tf_idf <- speeches_words %>%
  bind_tf_idf(word, name, n) %>% 
  select(-total) %>%
  arrange(desc(tf_idf))

library(forcats)

speech_tf_idf %>%
  group_by(name) %>%
  slice_max(tf_idf, n = 5, with_ties = FALSE) %>%
  ungroup() %>%
  ggplot(aes(tf_idf, fct_reorder(word, tf_idf), fill = name)) +
  geom_col(show.legend = FALSE) +
  facet_wrap(~name, ncol = 2, scales = "free") +
  labs(
    title = "Pięć najbardziej znaczących słów z każdego przemówienia",
    x = "tf-idf", 
    y = NULL) 

ggsave("speeches/tidytext/sentiment_via_speeches.png", width = 2000, height = 3000, units = "px")
