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


for (i in usi){
  camp <- subset(temp, sub==i)
  # The y-axis indicates the visibility probability of the target
  #キャンバスを用意して、gに格納
  g <- ggplot(camp, aes(y=cdt_test, x=cnd, color=as.character(test_eye))) +
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
#       geom_point(aes(color=as.character(test_eye)),
#                  position=position_jitter(width=0.3, height=0.06),
#                  alpha=0.4, shape=21) +
       stat_summary(aes(y=cdt_test, x=cnd), fun=mean,
                      geom="line", colour="black") +
       labs(color='test eye', subtitle=paste(i, 'test')) + ylim(0, 15)
  print(g)

    #キャンバスを用意して、gに格納
  g <- ggplot(camp, aes(y=cdt_sup, x=cnd, color=as.character(test_eye))) +
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
#       geom_point(aes(color=as.character(test_eye)),
#                  position=position_jitter(width=0.3, height=0.06),
#                  alpha=0.4, shape=21) +
       stat_summary(aes(y=cdt_sup, x=cnd), fun=mean,
                      geom="line", colour="black") +
       labs(color='test eye', subtitle=paste(i, 'sup')) + ylim(0, 15)
  print(g)
}

# observation time - (cdt_test + cdt_sup) meams cdt of diplopia
temp$cdt_dip <- 30 - (temp$cdt_sup + temp$cdt_test)
g <- ggplot(temp, aes(x=cnd, y=cdt_dip)) +
            stat_summary(fun=mean, geom="line") +
            stat_summary(aes(cnd),#種類ごとに
                         fun.data=mean_se,#mean_seで標準誤差、#mean_cl_normalで95%信頼区間(正規分布)
                         geom="errorbar",
                         size=0.5,#線の太さ
                         width=0.1) +
            xlab('size')

g


# The diff of cdt_test and cdt_sup
# この差が正ならば検査刺激の方が消失時間が長い
# サイズ条件間に見られる差は、検査刺激に早退して抑制刺激の消失のしにくさを示している
temp$diff <- (temp$cdt_test - temp$cdt_sup)
g <- ggplot(temp, aes(x=cnd, y=diff)) +
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
cols <- colorRamp(c("#0080ff","yellow","#ff8000"))
#function(key_press_list)
for (j in unique(camp$cnd)){
  # stringをtsvに変換
  onset <- subset(camp, cnd==j, c(press_timing_test, test_eye))
  onset$press_timing_test <- gsub('\\[]', '0', onset$press_timing_test)
  onset$press_timing_test <- gsub('\\[', '', onset$press_timing_test)
  onset$press_timing_test <- gsub(']', '', onset$press_timing_test)

  offset <- subset(camp, cnd==j, release_timing_test)
  offset$release_timing_test <- gsub('\\[]', '0', offset$release_timing_test)
  offset$release_timing_test <- gsub('\\[', '', offset$release_timing_test)
  offset$release_timing_test <- gsub(']', '', offset$release_timing_test)

  # tabで分割したリストをlong型に変形
  melt_onset <- strsplit(onset$press_timing_test, ' ') %>%
#    tidyr::pivot_longer(values_to = select(2,1)) #%>% select(2,1) %>% setNames(c("k","v"))
    reshape2::melt() %>% select(2,1) %>% setNames(c("k","v"))
  melt_onset$v <- as.numeric(as.character(melt_onset$v))
  melt_onset <- na.omit(melt_onset)

  melt_offset <- strsplit(offset$release_timing_test, ' ') %>%
#    tidyr::pivot_longer() %>% select(2,1) %>% setNames(c("k","v"))
    reshape2::melt() %>% select(2,1) %>% setNames(c("k","v"))
  melt_offset$v <- as.numeric(as.character(melt_offset$v))
  melt_offset <- na.omit(melt_offset)

  plot(0, type='n', xlim=c(0, 30), ylim=c(1, 6),
       main=paste('time table; size ', j), xlab='time', ylab='trials')
  segments(melt_onset$v, melt_onset$k, melt_offset$v, melt_offset$k)

  dotchart(melt_offset$v-melt_onset$v, col=rgb(cols(melt_onset$k/50)/255),
             main=j, xlim = c(0, 30), xlab='disappearance time')
}


for (j in unique(camp$cnd)){
  # stringをtsvに変換
  onset <- subset(camp, cnd==j, press_timing_sup)
  onset$press_timing_sup <- gsub('\\[]', '0', onset$press_timing_sup)
  onset$press_timing_sup <- gsub('\\[', '', onset$press_timing_sup)
  onset$press_timing_sup <- gsub(']', '', onset$press_timing_sup)

  offset <- subset(camp, cnd==j, release_timing_sup)
  offset$release_timing_sup <- gsub('\\[]', '0', offset$release_timing_sup)
  offset$release_timing_sup <- gsub('\\[', '', offset$release_timing_sup)
  offset$release_timing_sup <- gsub(']', '', offset$release_timing_sup)

  # tabで分割したリストをlong型に変形
  melt_onset <- strsplit(onset$press_timing_sup, ' ') %>%
#    tidyr::pivot_longer(values_to = select(2,1)) #%>% select(2,1) %>% setNames(c("k","v"))
    reshape2::melt() %>% select(2,1) %>% setNames(c("k","v"))
  melt_onset$v <- as.numeric(as.character(melt_onset$v))
  melt_onset <- na.omit(melt_onset)

  melt_offset <- strsplit(offset$release_timing_sup, ' ') %>%
#    tidyr::pivot_longer() %>% select(2,1) %>% setNames(c("k","v"))
    reshape2::melt() %>% select(2,1) %>% setNames(c("k","v"))
  melt_offset$v <- as.numeric(as.character(melt_offset$v))
  melt_offset <- na.omit(melt_offset)

  plot(0, type='n', xlim=c(0, 30), ylim=c(1, 6),
       main=paste('time table; size ', j), xlab='time', ylab='trials')
  segments(melt_onset$v, melt_onset$k, melt_offset$v, melt_offset$k)

  dotchart(melt_offset$v-melt_onset$v, col=rgb(cols(melt_onset$k/50)/255),
             main=j, xlim = c(0, 30), xlab='disappearance time')
}
