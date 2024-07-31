library(tidyverse)
library(Hmisc)
library(readxl)
library(readr)
library(extrafont)
library(rstatix)
library(sjmisc) # Round values in datasets
library(DBI)
library(RSQLite)
library(ggpubr)

# Database connection
db_path = "C://Users//User//Documents//Gaut//PostDoc//Manips//Directivité//manip_directivite//data//manip_directivite.db"
con <- dbConnect(RSQLite::SQLite(), dbname = db_path)
df <- dbGetQuery(con, 'SELECT users.id, rooms.name AS room, conditions.distance, conditions.angle, conditions.movement, conditions.source, recordings.repetition, sentences.amplitude, ratings.timbre AS answer_timbre, ratings.plausibility AS answer_plausibility, ratings.angle AS answer_angle, ratings.movement AS answer_movement
    FROM ratings 
    INNER JOIN recordings ON ratings.recording_id = recordings.id
    INNER JOIN rooms ON recordings.room_id = rooms.id
    INNER JOIN users ON ratings.user_id = users.id
    INNER JOIN conditions ON recordings.conditions_id = conditions.id
    INNER JOIN sentences ON recordings.sentence_id = sentences.id
    WHERE users.id > 1')

# Set factors
df <- df %>%
  convert_as_factor(id, room, distance, angle, movement, source, repetition)

# Compute z-scores
df$answer_plausibility <- ave(df$answer_plausibility, df$id, FUN = scale)
df$answer_timbre <- ave(df$answer_timbre, df$id, FUN = scale)

# Plots default theme
defaultFont <- element_text(color = "#4B5D67", size = 12, face = "bold")

defaultTheme <- theme_set(theme_minimal())

defaultTheme <- theme_set(theme_minimal()) +
  theme(text = defaultFont, axis.text = defaultFont, strip.text = defaultFont)

theme_set(defaultTheme)

# Boxplots
fig_boxplot_plausibility <- df %>%
  ggplot(aes(movement, answer_plausibility, colour = source)) +
  facet_grid(room ~ angle) +
  geom_boxplot(width = .1) +
  coord_cartesian(ylim=c(-3.,3.)) 
fig_boxplot_plausibility

fig_boxplot_timbre <- df %>%
  ggplot(aes(movement, answer_timbre, colour = source)) +
  facet_grid(room ~ angle) +
  geom_boxplot(width = .1) +
  coord_cartesian(ylim=c(-3.,3.)) 
fig_boxplot_timbre
  
# Mean + CI
fig_meanCIPlot_plausibility <- df %>%
  ggplot(aes(movement, answer_plausibility, colour = source)) +
  facet_grid(room ~ angle) +
  stat_summary(fun = mean, geom = "point", position = position_dodge(width = .1)) +
  stat_summary(fun.data = mean_cl_normal, geom = "errorbar", linewidth = 1, width = .1, position = "dodge") +
  coord_cartesian(ylim=c(-3.,3.))
fig_meanCIPlot_plausibility

fig_meanCIPlot_timbre <- df %>%
  ggplot(aes(movement, answer_timbre, colour = source)) +
  facet_grid(room ~ angle) +
  stat_summary(fun = mean, geom = "point", position = position_dodge(width = .1)) +
  stat_summary(fun.data = mean_cl_normal, geom = "errorbar", linewidth = 1, width = .1, position = "dodge") +
  coord_cartesian(ylim=c(-3.,3.))
fig_meanCIPlot_timbre

# QQ Plots
library(ggpubr)
fig_qqPlot_plausibility <- df %>%
  ggqqplot("answer_plausibility") +
  facet_grid(room + source + angle ~ movement + distance + amplitude, labeller = "label_both") +
  theme_set(defaultTheme)
fig_qqPlot_plausibility

fig_qqPlot_timbre <- df %>%
  ggqqplot("answer_timbre") +
  facet_grid(room + source + angle ~ movement + distance + amplitude, labeller = "label_both") +
  theme_set(defaultTheme)
fig_qqPlot_timbre

# Find Outliers
outliers_plausibility <- df %>%
  group_by(room, source, angle, movement, distance, amplitude) %>%
  identify_outliers(answer_plausibility)

outliers_timbre <- df %>%
  group_by(room, source, angle, movement, distance, amplitude) %>%
  identify_outliers(answer_timbre)

# Check Normality per cell (residuals are checked after the ANOVA)

shapiroWilk_plausibility <- df %>%
  group_by(room, source, angle, movement, distance, amplitude) %>%
  shapiro_test(answer_plausibility) %>%
  mutate(Sigp = ifelse(p > 0.05, "" , ifelse(p > 0.01, "*", ifelse(p > 0.01, "**", "***")))) %>%
  round_num(3)
View(shapiroWilk_plausibility)

shapiroWilk_timbre <- df %>%
  group_by(room, source, angle, movement, distance, amplitude) %>%
  shapiro_test(answer_timbre) %>%
  mutate(Sigp = ifelse(p > 0.05, "" , ifelse(p > 0.01, "*", ifelse(p > 0.01, "**", "***")))) %>%
  round_num(3)
View(shapiroWilk_timbre)

# ANOVA 
## PLAUSIBILITY

anovaResults_plausibility <- df %>%
  anova_test(dv = answer_plausibility, wid = id, within = c(room, source, angle, movement, distance, amplitude, repetition)) 

anovaResultsCorrected_plausibility <- get_anova_table(anovaResults_plausibility, correction = "auto") %>%
  round_num(3)

View(anovaResultsCorrected_plausibility)

## TIMBRE

anovaResults_timbre <- df %>%
  anova_test(dv = answer_timbre, wid = id, within = c(room, source, angle, movement, distance, amplitude, repetition)) 

anovaResultsCorrected_timbre <- get_anova_table(anovaResults_timbre, correction = "auto") %>%
  round_num(3)

View(anovaResultsCorrected_timbre)

# ANOVA Residuals

## PLAUSIBILITY

anovaResiduals_plausibility <- residuals(attr(anovaResults_plausibility, "args")$model)

groupedResiduals_plausibility <- data.frame(residuals = c(t(anovaResiduals_plausibility), stringAsFactors = F))

shapirowilkGroupedResiduals_plausibility <- groupedResiduals_plausibility %>%
  shapiro_test(residuals)

View(shapirowilkGroupedResiduals_plausibility)

fig_qqPlotResiduals_plausibility <- groupedResiduals_plausibility %>%
  ggqqplot("residuals")

## TIMBRE

anovaResiduals_timbre <- residuals(attr(anovaResults_timbre, "args")$model)

groupedResiduals_timbre <- data.frame(residuals = c(t(anovaResiduals_timbre), stringAsFactors = F))

shapirowilkGroupedResiduals_timbre <- groupedResiduals_timbre %>%
  shapiro_test(residuals)

View(shapirowilkGroupedResiduals_timbre)

fig_qqPlotResiduals_timbre <- groupedResiduals_timbre %>%
  ggqqplot("residuals")

# Simple effects of the source figure

fig_source_timbre <- df %>%
  ggplot(aes(source, answer_timbre)) +
  stat_summary(fun = mean, geom = "point", position = position_dodge(width = .1)) +
  stat_summary(fun.data = mean_cl_normal, geom = "errorbar", linewidth = 1, width = .1, position = "dodge") +
  coord_cartesian(ylim=c(-3.,3.))

fig_source_timbre

fig_source_plausibility <- df %>%
  ggplot(aes(source, answer_plausibility)) +
  stat_summary(fun = mean, geom = "point", position = position_dodge(width = .1)) +
  stat_summary(fun.data = mean_cl_normal, geom = "errorbar", linewidth = 1, width = .1, position = "dodge") +
  coord_cartesian(ylim=c(-3.,3.))

fig_source_plausibility

# Exemple interaction: Source x Room post-hoc (room moderator)
sourceXroom_roomModerator <- df %>%
  group_by(room) %>%
  pairwise_t_test(answer_plausibility ~ source, paired = TRUE, p.adjust.method = "bonferroni")

View(sourceXroom_roomModerator)

# Source x Room figure
fig_sourceXroom <- df %>%
  ggplot(aes(room, answer_plausibility, colour = source)) +
  stat_summary(fun = mean, geom = "point", position = position_dodge(width = .1)) +
  stat_summary(fun.data = mean_cl_normal, geom = "errorbar", linewidth = 1, width = .1, position = "dodge") +
  coord_cartesian(ylim=c(-3.,3.))
fig_sourceXroom

# ggsave(fig_source_plausibility, filename = "C:\\Users\\User\\Desktop\\source_plausibility.pdf", device = cairo_pdf)