# Title     : TODO
# Objective : TODO
# Created by: Mac1
# Created on: 2020/08/05
# List up files

library(ggplot2)

files <- list.files('correspond_type/data',full.names=T)
f <- length(files)

si <- gsub(".*(..)DATE.*","\\1", files)
n <- length(table(si))
usi <- unique(si)

# Load data and store
temp <- read.csv(files[1], stringsAsFactors = F)
temp$sub <- si[1]
temp$sn <- 1
for (i in 2:f) {
  d <- read.csv(files[[i]], stringsAsFactors = F)
  d$sub <- si[i]
  d$sn <- i
  temp <- rbind(temp, d)
}

# 検査刺激の消失時間を抽出(test_eye変数でclassfyされ、反応はcdt_l、r列に格納されている)
function(c) if (test_eye != 1) {cdt_test <- c} else {cdt_test <- c}

for (i in usi){
  camp <- subset(temp, sub==i)
  # The y-axis indicates the visibility probability of the target

  #キャンバスを用意して、gに格納
  g <- ggplot(camp, aes(y=cdt_r, x=cnd, color=as.character(test_eye))) +
       stat_summary(aes(x=cnd, color=as.character(test_eye)),
                    fun=mean, geom="point") +
       #折れ線グラフを描き入れる
       stat_summary(aes(cnd), #種類ごとに
                      fun=mean, #平均値を
                      geom="point",#点で
                      colour="black") +
       #エラーバーの追加
       stat_summary(aes(cnd),#種類ごとに
                      fun.data=mean_se,#mean_seで標準誤差、#mean_cl_normalで95%信頼区間(正規分布)
                      geom="errorbar",
                      size=0.5,#線の太さ
                      width=0.1) + #ぴょんって横に出てるアイツの幅
#       stat_smooth(method = "lm", formula = y~x, fullrange = T, se = T,alpha=0.1) +
       # 1が左眼、-1が右眼にターゲットを提示する
       geom_point(aes(color=as.character(test_eye)),
                  position=position_jitter(width=0.3, height=0.06),
                  alpha=0.4, shape=21) +
       stat_summary(aes(y=cdt_r, x=cnd), fun=mean,
                      geom="line", colour="black") +
       labs(color='test eye', subtitle=i)
  print(g)
}

# 全体平均
g <- ggplot(temp, aes(x=cnd, y=response)) +
            stat_summary(fun=mean, geom="line") +
            stat_summary(aes(cnd),#種類ごとに
                         fun.data=mean_se,#mean_seで標準誤差、#mean_cl_normalで95%信頼区間(正規分布)
                         geom="errorbar",
                         size=0.5,#線の太さ
                         width=0.1) +
            xlab('size')

g

library(tidyr)
# ANOVA
df <- aggregate(temp$response, by=temp[c('sub', 'cnd')], FUN=mean)
df_shaped <- pivot_wider(df, names_from=cnd, values_from=x)
df_shaped$sub <- NULL

#ANOVA <- aov(x~cnd*eccentricity, df)
#summary(ANOVA)

source('anovakun_485.txt')
ANOVA <- anovakun(df_shaped, 'sA', 4, holm=T, peta=T)


library("reshape2")
# Particular disapperance times
par(mfrow=c(2,2))
cols = colorRamp(c("#0080ff","yellow","#ff8000"))
#function(key_press_list)
for (j in unique(camp$cnd)){
  onset <- subset(camp, cnd==j, press_timing_test)
  onset$press_timing_test <- gsub('\\[]', '0', onset$press_timing_test)
  onset$press_timing_test <- gsub('\\[', '', onset$press_timing_test)
  onset$press_timing_test <- gsub(']', '', onset$press_timing_test)

  offset <- subset(camp, cnd==j, release_timing_test)
  offset$release_timing_test <- gsub('\\[]', '0', offset$release_timing_test)
  offset$release_timing_test <- gsub('\\[', '', offset$release_timing_test)
  offset$release_timing_test <- gsub(']', '', offset$release_timing_test)

  melt_onset <- strsplit(onset$press_timing_test, ' ') %>%
    reshape2::melt() %>% select(2,1) %>% setNames(c("k","v"))
  melt_onset$v <- as.numeric(as.character(melt_onset$v))
  melt_onset <- na.omit(melt_onset)

  melt_offset <- strsplit(offset$release_timing_test, ' ') %>%
    reshape2::melt() %>% select(2,1) %>% setNames(c("k","v"))
  melt_offset$v <- as.numeric(as.character(melt_offset$v))
  melt_offset <- na.omit(melt_offset)

  plot(0, type='n', xlim=c(0, 30), ylim=c(1, 5),
       main=paste('time table; width ', j), xlab='time', ylab='trials')
  segments(melt_onset$v, melt_onset$k, melt_offset$v, melt_offset$k)

  dotchart(melt_offset$v-melt_onset$v, col=rgb(cols(melt_onset$k/50)/255),
             main=j, xlim = c(0, 30), xlab='disappearance time')
}
