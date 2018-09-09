
Auto=read.csv("~/proj_stats202/training.csv",header=T)
fix(Auto)
attach(Auto)

Auto=na.omit(Auto)

Auto$query_length = as.factor(query_length)
Auto$is_homepage = as.factor(is_homepage)

#rank = c()
#number = c
#previous_q = query_id[0]
#temp_count = 0
#for (i in 1:80046) {
#  current_q = query_id[i]
#}

cor(Auto)

new_sig3 = c()
for(i in 1:80046) {
  if (sig3[i] != 0) {
    new_sig3[i] <- log(sig3[i])
  }
}

new_sig4 = c()
for(i in 1:80046) {
  if (sig4[i] != 0) {
    new_sig4[i] <- log(sig4[i])
  }
}

new_sig5 = c()
for(i in 1:80046) {
  if (sig5[i] != 0) {
    new_sig5[i] <- log(sig5[i])
  }
}

new_sig6 = c()
for(i in 1:80046) {
  if (sig6[i] != 0) {
    new_sig6[i] <- log(sig6[i])
  }
}


glm.fit = glm(relevance ~ sig1 + sig2 + new_sig3 + new_sig4 + new_sig5 + new_sig6 +
                sig7 + sig8 + as.factor(is_homepage) + as.factor(query_length)
                , data = Auto)
summary(glm.fit)

train = c(1:72070)
test = c(72071:80046)

x = model.matrix(relevance ~  sig1 + sig2 + new_sig3 + new_sig4 + new_sig5 + new_sig6 +
                   sig7 + sig8 + as.factor(is_homepage) + as.factor(query_length), Auto)[, -1]
y = Auto$relevance

x_train = x[train, ]
y_train = y[train]

x_test = x[test, ]
y_test = y[test] # len 7976

glm.fit1 = glm(relevance ~ .,
               data = Auto, family = binomial, subset = train
)
train.dat = data.frame(x = x_test)
glm.probs = predict(glm.fit3, train.dat, type = "response")

glm.pred = rep(0, 7976)
for (i in 1:7976) {
  if(glm.probs[i + 72071 - 1] > 0.5) {
    glm.pred[i] = 1
  }
}
table(glm.pred, y_test)
mean(glm.pred == y_test)

library(e1071)
dat_train = data.frame(x = x_train, y_train)
svmfit = svm(y_train~ ., data = dat_train,
                kernel = 'radial', cost = 0.01, scale = FALSE)
summary(svmfit)

testdat = data.frame(x = x_test, y_test)
ytestpred = predict(svmfit, testdat)

#mean((ytestpred == y_test)^2)
count_right = 0
for (i in 1:23662) {
  if (ytestpred[i] == y_test[i]) {
    count_right = count_right + 1;
  }
}
count_wrong / 23662

