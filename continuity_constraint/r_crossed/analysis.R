# Title     : TODO
# Objective : TODO
# Created by: Mac1
# Created on: 2020/08/05
# List up files

library(ggplot2)
#library(ggpmisc)

files <- list.files('continuity_constraint/r_crossed/data',full.names=T)
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
#temp$cnd <- temp$cnd*3.6

# 検査眼が反転している被験者の視差を反転
temp$cnd[temp$cnd==3] <- -3

#slopes <- data.frame(rep(NA, 5), nrow=1)[numeric(0), ]
for (i in usi){
  camp <- subset(temp, sub==i)
  # The y-axis indicates the visibility probability of the target

  #キャンバスを用意して、gに格納
  g <- ggplot() +
       # 折れ線グラフを描き入れる
       stat_summary(aes(y=camp$cdt, x=camp$cnd), fun=mean, geom="line", colour="black") +
       # エラーバーの追加
       stat_summary(aes(y=camp$cdt, x=camp$cnd), fun.data=mean_se, geom="errorbar", size=0.5, width=0.5) +
       # 試行ごとのデータを表示, -1が左眼、1が右眼にターゲットを提示
       geom_point(aes(y=camp$cdt, x=camp$cnd), position=position_jitter(width=0.3, height=0), alpha=0.4, shape=21) +

       # ラベルの整形
       labs(subtitle=i, color='eye') + xlab('distance') + theme(text = element_text(size = 20)) +
       ylim(0, 30)
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
