# Title     : TODO
# Objective : TODO
# Created by: Mac1
# Created on: 2020/08/05
# List up files

library(ggplot2)

files <- list.files('SSuppR/local/data',full.names=T)
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

# cndの正負を均す、水平位置は違うがどちらも提示眼の条件によって交差視差となるので
temp$cnd <- sqrt(temp$cnd^2)

for (i in usi){
  camp <- subset(temp, sub==i)
  # The y-axis indicates the visibility probability of the target

  #キャンバスを用意して、gに格納
  g <- ggplot(camp, aes(y=cdt, x=cnd, color=as.character(test_eye))) +
       stat_summary(aes(cnd, color=as.character(test_eye)),
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
       # -1が左眼、1が右眼にターゲットを提示する
       geom_point(aes(color=as.character(test_eye)),
                  position=position_jitter(width=0.3, height=0.06),
                  alpha=0.4, shape=21) +
       stat_summary(aes(y=cdt, x=cnd), fun=mean,
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
