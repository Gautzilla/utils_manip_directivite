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
library(xtable) # Export tables to LaTeX: xtable(anovaResults)

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
dbDisconnect(con)

# Set factors
df <- df %>%
  convert_as_factor(id, room, distance, angle, movement, source, repetition)

# Group by repetition
df <- df %>%
  group_by(id, room, distance, angle, movement, source, amplitude) %>%
  summarise(across(-repetition, mean, na.rm = TRUE)) 
df <- df %>%
  as_data_frame()

# Merge Movement and Amplitude factors
df$stimulus <- paste(df$movement, df$amplitude)
df <- df %>%
  mutate(stimulus = recode(stimulus, '0 Small' = 'Sta1', '0 Large' = 'Sta2', '1 Small' = 'Dyn1', '1 Large' = 'Dyn2'))

df <- df[, c('id', 'room', 'distance', 'angle', 'stimulus', 'source', 'answer_plausibility', 'answer_timbre', 'answer_angle', 'answer_movement')]

# Compute z-scores
df$answer_plausibility <- ave(df$answer_plausibility, df$id, FUN = scale)
df$answer_timbre <- ave(df$answer_timbre, df$id, FUN = scale)

# Plots default theme
defaultFont <- element_text(color = "#4B5D67", size = 12, face = "bold")

defaultTheme <- theme_set(theme_minimal())

defaultTheme <- theme_set(theme_minimal()) +
  theme(text = defaultFont, axis.text = defaultFont, strip.text = defaultFont)

theme_set(defaultTheme)

# Correlation

plot(df$answer_plausibility, df$answer_timbre)

df %>%
  dplyr::summarize(correlation = cor(answer_plausibility, answer_timbre))
cor.test(df$answer_plausibility, df$answer_timbre)
# Boxplots
df %>%
  ggplot(aes(source, answer_plausibility, colour = stimulus)) +
  facet_grid(room ~ angle + distance) +
  geom_boxplot(width = .1) +
  coord_cartesian(ylim=c(0.,1.))

fig_boxplot_plausibility <- df %>%
  ggplot(aes(movement, answer_plausibility, colour = source)) +
  facet_grid(room ~ angle) +
  geom_boxplot(width = .1) +
  coord_cartesian(ylim=c(-3.,3.))

fig_boxplot_timbre <- df %>%
  ggplot(aes(movement, answer_timbre, colour = source)) +
  facet_grid(room ~ angle) +
  geom_boxplot(width = .1) +
  coord_cartesian(ylim=c(-3.,3.))
  
# Mean + CI
fig_meanCIPlot_plausibility <- df %>%
  ggplot(aes(movement, answer_plausibility, colour = source)) +
  facet_grid(room ~ angle) +
  stat_summary(fun = mean, geom = "point", position = position_dodge(width = .1)) +
  stat_summary(fun.data = mean_cl_normal, geom = "errorbar", linewidth = 1, width = .1, position = "dodge") +
  coord_cartesian(ylim=c(-3.,3.))

fig_meanCIPlot_timbre <- df %>%
  ggplot(aes(movement, answer_timbre, colour = source)) +
  facet_grid(room ~ angle) +
  stat_summary(fun = mean, geom = "point", position = position_dodge(width = .1)) +
  stat_summary(fun.data = mean_cl_normal, geom = "errorbar", linewidth = 1, width = .1, position = "dodge") +
  coord_cartesian(ylim=c(-3.,3.))

# QQ Plots
fig_qqPlot_plausibility <- df %>%
  ggqqplot("answer_plausibility") +
  facet_grid(room + source + angle ~ movement + distance + amplitude, labeller = "label_both") +
  theme_set(defaultTheme)

fig_qqPlot_timbre <- df %>%
  ggqqplot("answer_timbre") +
  facet_grid(room + source + angle ~ movement + distance + amplitude, labeller = "label_both") +
  theme_set(defaultTheme)

# Find Outliers
outliers_plausibility <- df %>%
  group_by(room, source, angle, movement, distance) %>%
  identify_outliers(answer_plausibility)

outliers_timbre <- df %>%
  group_by(room, source, angle, movement, distance) %>%
  identify_outliers(answer_timbre)

# Check Normality per cell (residuals are checked after the ANOVA)

shapiroWilk_plausibility <- df %>%
  group_by(room, source, angle, stimulus, distance) %>%
  shapiro_test(answer_plausibility) %>%
  mutate(Sigp = ifelse(p > 0.05, "" , ifelse(p > 0.01, "*", ifelse(p > 0.01, "**", "***")))) %>%
  round_num(3)

shapiroWilk_timbre <- df %>%
  group_by(room, source, angle, stimulus, distance) %>%
  shapiro_test(answer_timbre) %>%
  mutate(Sigp = ifelse(p > 0.05, "" , ifelse(p > 0.01, "*", ifelse(p > 0.01, "**", "***")))) %>%
  round_num(3)

# ANOVA : results and corrected results are not piped so that residuals can be catched

## PLAUSIBILITY

anovaResults_plausibility <- df %>%
  anova_test(dv = answer_plausibility, wid = id, within = c(room, source, angle, stimulus, distance)) 

anovaResultsCorrected_plausibility <- get_anova_table(anovaResults_plausibility, correction = "auto") %>%
  round_num(3)

xtable(anovaResultsCorrected_plausibility, digits = c(0,0,1,1,1,3,3,3))

## TIMBRE

anovaResults_timbre <- df %>%
  anova_test(dv = answer_timbre, wid = id, within = c(room, source, angle, stimulus, distance)) 

anovaResultsCorrected_timbre <- get_anova_table(anovaResults_timbre, correction = "auto") %>%
  round_num(3)

xtable(anovaResultsCorrected_timbre, digits = c(0,0,1,1,1,3,3,3))

# ANOVA Residuals

## PLAUSIBILITY

anovaResiduals_plausibility <- residuals(attr(anovaResults_plausibility, "args")$model)

groupedResiduals_plausibility <- data.frame(residuals = c(t(anovaResiduals_plausibility), stringAsFactors = F))

shapirowilkGroupedResiduals_plausibility <- groupedResiduals_plausibility %>%
  shapiro_test(residuals)

fig_qqPlotResiduals_plausibility <- groupedResiduals_plausibility %>%
  ggqqplot("residuals")

## TIMBRE

anovaResiduals_timbre <- residuals(attr(anovaResults_timbre, "args")$model)

groupedResiduals_timbre <- data.frame(residuals = c(t(anovaResiduals_timbre), stringAsFactors = F))

shapirowilkGroupedResiduals_timbre <- groupedResiduals_timbre %>%
  shapiro_test(residuals)

fig_qqPlotResiduals_timbre <- groupedResiduals_timbre %>%
  ggqqplot("residuals")

# Simple effects of the source figure

df %>%
  ggplot(aes(source, answer_timbre)) +
  stat_summary(fun = mean, geom = "point", position = position_dodge(width = .1)) +
  stat_summary(fun.data = mean_cl_normal, geom = "errorbar", linewidth = 1, width = .1, position = "dodge") +
  coord_cartesian(ylim=c(-3.,3.))

df %>%
  ggplot(aes(source, answer_plausibility)) +
  stat_summary(fun = mean, geom = "point", position = position_dodge(width = .1)) +
  stat_summary(fun.data = mean_cl_normal, geom = "errorbar", linewidth = 1, width = .1, position = "dodge") +
  coord_cartesian(ylim=c(-3.,3.))

# Plausibility interaction: Source x Stimulus
df %>%
  ggplot(aes(source, answer_plausibility, colour = stimulus)) +
  stat_summary(fun = mean, geom = "point", position = position_dodge(width = .1)) +
  stat_summary(fun.data = mean_cl_normal, geom = "errorbar", linewidth = 1, width = .1, position = "dodge") +
  coord_cartesian(ylim=c(-1.,1.))

ph <- df %>%
  group_by(source) %>%
  pairwise_t_test(answer_plausibility ~ stimulus, paired = TRUE)
ph$p_adj <- ph$p * 12

cohens <- df %>%
  group_by(source) %>%
  cohens_d(answer_plausibility ~ stimulus, paired = TRUE)

ph_tot <- cbind(x = ph[, c('source', 'group1', 'group2', 'p_adj')], y = cohens[, c('effsize')])

xtable(ph_tot, digits = c(0, 0, 0, 0, 3, 3))

# Plausibility interaction: Angle x Stimulus x Distance
df %>%
  ggplot(aes(angle, answer_plausibility, colour = stimulus)) +
  facet_wrap(. ~ distance) +
  stat_summary(fun = mean, geom = "point", position = position_dodge(width = .1)) +
  stat_summary(fun.data = mean_cl_normal, geom = "errorbar", linewidth = 1, width = .1, position = "dodge") +
  coord_cartesian(ylim=c(-1.,1.))

ph <- df %>%
  group_by(angle, distance) %>%
  pairwise_t_test(answer_plausibility ~ stimulus, paired = TRUE)
ph$p_adj <- ph$p * 24

cohens <- df %>%
  group_by(angle, distance) %>%
  cohens_d(answer_plausibility ~ stimulus, paired = TRUE)

ph_tot <- cbind(x = ph[, c('distance', 'angle', 'group1', 'group2', 'p_adj')], y = cohens[, c('effsize')])

xtable(ph_tot, digits = c(0, 0, 0, 0, 0, 3, 3))

# Timbre interaction: Angle x Stimulus x Distance
df %>%
  ggplot(aes(room, answer_timbre, colour = angle)) +
  facet_wrap(. ~ source) +
  stat_summary(fun = mean, geom = "point", position = position_dodge(width = .1)) +
  stat_summary(fun.data = mean_cl_normal, geom = "errorbar", linewidth = 1, width = .1, position = "dodge") +
  coord_cartesian(ylim=c(-1.,1.5))

# Timbre interaction: Angle x Stimulus x Distance
df %>%
  ggplot(aes(angle, answer_timbre, colour = stimulus)) +
  facet_wrap(. ~ distance) +
  stat_summary(fun = mean, geom = "point", position = position_dodge(width = .1)) +
  stat_summary(fun.data = mean_cl_normal, geom = "errorbar", linewidth = 1, width = .1, position = "dodge") +
  coord_cartesian(ylim=c(-1.,1.5))

# Direct questions: Angle x Stimulus x Distance
df %>%
  ggplot(aes(source, answer_angle, colour = stimulus)) +
  facet_wrap(. ~ angle) +
  stat_summary(fun = mean, geom = "point", position = position_dodge(width = .1)) +
  stat_summary(fun.data = mean_cl_normal, geom = "errorbar", linewidth = 1, width = .1, position = "dodge") +
  coord_cartesian(ylim=c(0.,1.))
