library(tidyverse)
library(rvest)
library(xml2)
# 
# 
# "itt egy feladatitt egy feladat" --> "itt egy feladat"
felez <- function(tt) tt |> str_replace("(^.*)\\1$", "\\1")
# 
# a könyvtár a [gtrends.zip]ből:
konyvtar <- "gtrends"
# 
# a [github action]-nel mentett [html]-ek:
files <- konyvtar |> 
  list.files(pattern = "^gtrends.+_[a-c]\\.html$", full.names = TRUE)
# 
# egy [list] minden egyes [html] fájlról:
trending_heads <- files |> 
  map(
    ~ .x |> 
      read_html() |> 
      html_nodes("table, tbody tr") |> 
      html_text2() |> 
      str_trim() |> 
      str_replace_all("\\n·\\n", "\n") |> 
      # str_replace_all("\\+ keresés(\\n[\\p{L}_]+){2}", "+") |> 
      str_split_fixed("\\n\\t\\n", 4) |>                          # TODO: 4
      as_tibble(.name_repair = ~ letters[1:length(.x)])|> 
      separate_wider_delim(
        a, 
        delim = "\n",                                     # ez CSAK szimpla
        names = LETTERS[1:5], names_sep = "_",
        too_few = "align_start") |>                               # TODO: 5
      separate_wider_delim(
        b:c, 
        delim = "\n",                                     # ez CSAK szimpla
        names = LETTERS[1:3], names_sep = "_",
        too_few = "align_start") |>                               # TODO: 3
      mutate(
        d = d |> 
          str_remove_all("Keresési kifejezésquery_statsFelfedezés") |> 
          str_split("\\n") |> 
          map(~ .x |> felez() |> paste(collapse = "; "))
      ) |> 
      unnest(d) |> 
      # ha hiányos az [a_B] oszlop, nem kell -- az első két sor
      filter(!is.na(a_B)) |> 
      mutate(
        timestamp = .x |> 
          str_extract_all("\\d") |> 
          unlist() |> 
          paste(collapse = "") |> 
          ymd_hms() |> 
          with_tz(tzone = "Europe/Budapest"),
        ab = .x |> 
          str_sub(-6, -6),
        id = 1:n(),
        .before = a_A
      )
    )
# 
# az előbbi [list]ből egy [tibble]:
trending_details <- trending_heads |> 
  bind_rows() |> 
  select(!ab) |> 
  mutate(
    id = 1:n(),
    .by = timestamp
  )
trending_details |> 
  summarise(
    nrow = max(id),
    .by = timestamp
  )
trending_details |> 
  write_tsv("trending_now.tsv")
