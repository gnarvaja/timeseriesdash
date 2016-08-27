#install.packages("Quandl")
#setwd("~/dev/timeseriesdash/R/")
library(Quandl)
getQuandl<-function(tick,description=""){
  ret<-Quandl(tick)
  #head(ret)
  if (names(ret)[1]!="Date"){
    print(paste("Se corrige nombre de campo",names(ret)[1], "a Date"))
    names(ret)[1]<-"Date"
  }
  if (names(ret)[2]!="Value"){
    print(paste("Se corrige nombre de campo",names(ret)[2], "a Value"))
    names(ret)[2]<-"Value"
  }
  ret<-cbind(symbol=rep(tick,nrow(ret)),src=rep("Quandl",nrow(ret)),description=rep(description,nrow(ret)),ret)
  #head(ret)
  ret
}

getAggData<-function(data){
  data.agg.min.date<-aggregate(data$Date,by=list(symbol=data$symbol,description=data$description),FUN=min)
  names(data.agg.min.date)[3]<-"min.date"
  data.agg.max.date<-aggregate(data$Date,by=list(symbol=data$symbol,description=data$description),FUN=max)
  names(data.agg.max.date)[3]<-"max.date"
  data.agg.max.count<-aggregate(data$Date,by=list(symbol=data$symbol,description=data$description),FUN=length)
  names(data.agg.max.count)[3]<-"count"
  data.agg<-merge(data.agg.min.date,data.agg.max.date)
  data.agg<-merge(data.agg,data.agg.max.count)
  data.agg
}

#Petroleo OPEC
data<-getQuandl("OPEC/ORB","Petroleo OPEC")
names(data)
data<-rbind(data,getQuandl("WGC/GOLD_DAILY_USD","Oro"))
#https://www.quandl.com/data/WGC/GOLD_DAILY_USD-Gold-Prices-Daily-Currency-USD
data<-rbind(data,getQuandl("BLSI/SUUR0000SA0", "IPC EEUU NG"))
#https://www.quandl.com/data/BLSI/SUUR0000SA0-Chained-CPI-All-Urban-Consumers-All-items
data<-rbind(data,getQuandl("COM/WLD_COCONUT_OIL","Aceite Coco"))
#https://www.quandl.com/data/COM/WLD_COCONUT_OIL-Coconut-oil-Price-mt
data<-rbind(data,getQuandl("COM/WLD_SOYBEAN_OIL","Aceite de Soja"))
#https://www.quandl.com/data/COM/WLD_SOYBEAN_OIL-Soybean-oil-Price-mt
data<-rbind(data,getQuandl("COM/WLD_SOYBEANS","Poroto de Soja"))
#https://www.quandl.com/data/COM/WLD_SOYBEANS-Soybeans-Price-mt
data<-rbind(data,getQuandl("COM/WLD_SOYBEAN_MEAL","Harina de Soja"))
#https://www.quandl.com/data/COM/WLD_SOYBEAN_MEAL-Soybean-meal-Price-mt
data<-rbind(data,getQuandl("COM/WLD_WHEAT_US_HRW","Trigo"))
#https://www.quandl.com/data/COM/WLD_WHEAT_US_HRW-Wheat-Price-US-HRW-mt
data<-rbind(data,getQuandl("COM/WLD_SILVER","Plata"))
#https://www.quandl.com/data/COM/WLD_MAIZE-Maize-Price-mt
data<-rbind(data,getQuandl("COM/WLD_MAIZE","Maiz"))
#data$src<-"Quandl"
write.table(data,"../data/commodities.csv",row.names = FALSE,sep=",",quote=FALSE)

agg.data<-getAggData(data)
agg.data
