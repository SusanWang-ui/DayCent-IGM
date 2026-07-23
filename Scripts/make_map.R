library(ggplot2)
library(maps)
library(ggrepel)
library(dplyr)

#wd <- "D:/comet-farm-daycent-model-source-code-main/Test with exp sites/mt"
wd <- "C:/Users/Derek.Pierson/OneDrive - Agoro Carbon Alliance/Carbon Modeling Team/RM_DayCent_IGM_Paper/mt"
setwd(wd)

df_kfold <- read.csv("k_fold_con.csv")

subdirs <- list.dirs(path = "multi_main", recursive = FALSE, full.names = TRUE)

sites <- c()
lats <- c()
lons <- c()

for (subdir in subdirs) {
  files <- list.files(path = subdir, pattern = "\\_soil.txt$", full.names = TRUE)
  soil_file <- files[1]
  
  line <- readLines(soil_file, n = 1)
  parts <- strsplit(trimws(line), "\\s+")[[1]]
  
  site <- basename(subdir)
  lat <- as.numeric(parts[2])
  lon <- as.numeric(parts[3])
  
  sites <- c(sites, site)
  lats <- c(lats, lat)
  lons <- c(lons, lon)
}

df_sites <- data.frame(
  site_name = sites,
  lat = lats,
  lon = lons
)

# Identify which fold is validation (value == 0)
df_fold <- df_kfold %>%
  mutate(
    validation_fold = case_when(
      fold01 == 0 ~ "Fold 1",
      fold02 == 0 ~ "Fold 2",
      fold03 == 0 ~ "Fold 3"
    )
  ) %>%
  distinct(site_name, validation_fold)

# Merge coordinates with fold info
df_map <- left_join(df_sites, df_fold, by = "site_name")

world_map <- map_data("world")

# Plot
map <- ggplot() +
  geom_polygon(
    data = world_map,
    aes(x = long, y = lat, group = group),
    fill = "gray90",
    color = "white"
  ) +
  geom_point(
    data = df_map,
    aes(x = lon, y = lat, color = validation_fold),
    size = 3
  ) +
  geom_text_repel(
    data = df_map,
    aes(x = lon, y = lat, label = site_name),
    size = 3,
    max.overlaps = 1000
  ) +
  coord_fixed(1.3) +
  scale_x_continuous(breaks = seq(-180, 180, 30)) +
  scale_y_continuous(breaks = seq(-90, 90, 30)) +
  scale_color_manual(
    values = c(
      "Fold 1" = "red",
      "Fold 2" = "blue",
      "Fold 3" = "darkgreen"
    )
  ) +
  labs(
    x = NULL,
    y = NULL
  ) +
  theme_minimal() +
  theme(
    axis.title = element_text(size = 11),
    axis.text = element_text(size = 9),
    legend.title = element_blank(),
    legend.position = c(0.02, 0.02),
    legend.justification = c(0, 0),
    legend.background = element_rect(fill = alpha("white", 0.7), color = NA)
  )

map

ggsave(
  "map_600dpi.png",
  plot = map,
  width = 6.5,
  height = 3.25,
  units = "in",
  dpi = 600,
  bg = "white"
)