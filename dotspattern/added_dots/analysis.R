# Title     : TODO
# Objective : TODO
# Created by: Mac1
# Created on: 2020/08/05
# List up files

library(ggplot2)
#library(ggpmisc)

files <- list.files('dotspattern/added_dots/data',full.names=T)
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

# cndの数値をmin of arcに変換, * 3.6 min
temp$cnd <- temp$cnd*3.6

#slopes <- data.frame(rep(NA, 5), nrow=1)[numeric(0), ]
for (i in usi){
  camp <- subset(temp, sub==i & continuity==0)
  camp2 <- subset(temp, sub==i & continuity!=0)
  # The y-axis indicates the visibility probability of the target

  #キャンバスを用意して、gに格納
  g <- ggplot() +
       # 折れ線グラフを描き入れる
       stat_summary(aes(y=camp$cdt, x=camp$cnd, shape='alone'), fun=mean, geom="point", colour="black", show.legend=FALSE) +
       stat_summary(aes(y=camp$cdt, x=camp$cnd, linetype='alone'), fun=mean, geom="line", colour="black") +
       # エラーバーの追加
       stat_summary(aes(y=camp$cdt, x=camp$cnd), fun.data=mean_se, geom="errorbar", size=0.5, width=0.5) +
       # 試行ごとのデータを表示, -1が左眼、1が右眼にターゲットを提示
       geom_point(aes(y=camp$cdt, x=camp$cnd, color=as.character(camp$test_eye)), position=position_jitter(width=0.3, height=0), alpha=0.4, shape=21) +

       # 折れ線グラフを描き入れる
       stat_summary(aes(y=camp2$cdt, x=camp2$cnd, shape='array'), fun=mean, geom="point", colour="black", show.legend=FALSE) +
       stat_summary(aes(y=camp2$cdt, x=camp2$cnd, linetype='array'), fun=mean, geom="line", colour="black") +
       # エラーバーの追加
       stat_summary(aes(y=camp2$cdt, x=camp2$cnd), fun.data=mean_se, geom="errorbar", size=0.5, width=0.5) +
       # 試行ごとのデータを表示, -1が左眼、1が右眼にターゲットを提示
       geom_point(aes(y=camp2$cdt, x=camp2$cnd, color=as.character(camp2$test_eye)), position=position_jitter(width=0.3, height=0), alpha=0.4, shape=24, show.legend=FALSE) +

       # ラベルの整形
       labs(subtitle=i, color='eye') + xlab('distance') + theme(text = element_text(size = 20)) +
       xlim(-1, max(camp$cnd)+1) + ylim(0, 30)
  print(g)

#  b <- lm(cdt~cnd, camp)
#  sl <- summary.lm(b)
#  slopes <- rbind(slopes, sl$coefficients[2, ])
}


# 全体平均
g <- ggplot(temp, aes(x=cnd, y=cdt)) +
  stat_summary(fun=mean, geom="line") +
  stat_summary(aes(cnd),#種類ごとに
               fun.data=mean_se,#mean_seで標準誤差、#mean_cl_normalで95%信頼区間(正規分布)
               geom="errorbar",
               size=0.5,#線の太さ
               width=0.5) +
  stat_summary(aes(color=sub, label=sub), fun=mean, geom='text', alpha=0.4) +
  xlab('disparity') + theme(text = element_text(size = 24), legend.position = 'none')

g

library(tidyr)
# ANOVA
df <- aggregate(temp$cdt, by=temp[c('sub', 'cnd')], FUN=mean)
df_shaped <- pivot_wider(df, names_from=cnd, values_from=x)
df_shaped$sub <- NULL

#ANOVA <- aov(x~cnd*eccentricity, df)
#summary(ANOVA)

source('anovakun_485.txt')
capture.output(anovakun(df_shaped, "sA", 4, holm=T, peta=T), file = "SSuppR2/local/anova_output.txt")
