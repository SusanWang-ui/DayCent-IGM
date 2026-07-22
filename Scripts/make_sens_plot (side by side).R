library(ggplot2)
library(patchwork)
library(forcats)

make_plot <- function(wd_path, title_text, letter, x_pos, l_pos) {
  setwd(wd_path)
  
  df <- read.csv("all_sa.csv")
  
  new_colnames <- c()
  for (i in colnames(df)) {
    if (i == colnames(df)[1]) {
      new_colnames <- c(new_colnames, "var")
    } else {
      new_colnames <- c(new_colnames, paste0(gsub(".1", "", i), "_", df[1,i]))
    }
  }
  colnames(df) <- new_colnames
  df <- df[-1, ]
  
  selected_cols <- c("var")
  for (i in colnames(df)) {
    if (grepl("ST", i)) {
      selected_cols <- c(selected_cols, i)
    }
  }
  df <- df[selected_cols]
  
  result_list <- list()
  for (i in colnames(df)) {
    if (i != "var") {
      df_temp <- df[c("var", i)]
      df_temp$site <- i
      colnames(df_temp) <- c("var", "value", "site")
      result_list[[i]] <- df_temp
    }
  }
  
  final_df <- do.call(rbind, result_list)
  rownames(final_df) <- NULL
  final_df$value <- as.numeric(final_df$value)
  var_order <- names(sort(tapply(final_df$value, final_df$var, mean), decreasing = TRUE))
  final_df$var <- factor(final_df$var, levels = var_order)
  final_df$site <- gsub("_ST", "", final_df$site)
  
  print(var_order)
  
  xintercept = 10.5
  y_breaks <- seq_along(levels(final_df$var))
  y_labels <- levels(final_df$var)
  
  g <- ggplot(final_df, aes(x = value, y = var, color = site)) +
    geom_point(size = 3, alpha = 0.8) +
    # geom_hline(yintercept = if (l_pos == "none") 8.5 else 13.5, linetype = "dashed", color = "black", linewidth = 0.4) +  # <-- added line
    scale_x_continuous(limits = c(0, 1)) +
    scale_y_discrete(limits = rev(y_labels)) +
    labs(
      y = "Parameter names",
      x = expression(S[Ti]),
      color = "Sites",
      title = title_text
    ) +
    labs(tag = letter) +
    theme_bw() +
    theme(
      plot.tag.position = c(0.95, 0.93),
      plot.tag = element_text(size = 12, face = "bold"),
      axis.text.x = element_text(size = 9, angle = 90, vjust = 0.5, hjust = 1),
      axis.title.x = element_text(size = 11),
      legend.title = element_text(size = 8),
      legend.text = element_text(size = 8),
      legend.key.height = unit(0.8, "lines"),
      legend.spacing.y = unit(0.2, "lines"),
      legend.position = "none",
      axis.text.y  = element_text(size = 9),
      axis.title.y = element_text(size = 11)
    )
  
  return(g)
}


wd1 <- "D:/comet-farm-daycent-model-source-code-main/Test with exp sites/mt/multi_main_ORG"
wd2 <- "D:/comet-farm-daycent-model-source-code-main/Test with exp sites/mt/multi_main_MOD"

plot1 <- make_plot(wd1, "DayCent", "A", 0.7, "none")
plot2 <- make_plot(wd2, "DayCent-IGM", "B", 0.7, "right")


setwd("D:/comet-farm-daycent-model-source-code-main/Test with exp sites")
combined_plot <- (plot1 | plot2) +
  plot_layout(guides = "collect") &
  theme(legend.position = "bottom",
        legend.justification = "right",
        #legend.box.just = "left",
        legend.spacing.x = unit(0.1, "lines"),
        legend.spacing.y = unit(0, "lines"),
        legend.key.width = unit(0.8, "lines"),
        legend.key.height = unit(0.8, "lines"),
        legend.margin = margin(0, 0, 0, 0)) & 
  guides(color = guide_legend(ncol = 5,
                              byrow = TRUE,
                              override.aes = list(size = 3)))

ggsave(
  "sens_plot_combined.png",
  plot = combined_plot,
  width = 6.5,
  height = 6.5,   # taller since stacked
  units = "in",
  dpi = 300
)