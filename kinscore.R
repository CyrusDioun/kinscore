library('synbreed', lib.loc=".")

data <- read.csv('data/synbreed_input.csv')
pedigree <- create.pedigree(ID=data$id, Par1=data$par1, Par2=data$par2)
gp <- create.gpData(pedigree=pedigree)
score <- kin(gpData=gp, ret='add')

name <- read.csv('data/synbreed_id.csv')

output <- t(apply(expand.grid(name$id, name$id), 1, function(x) {c(as.character(name[name$id==as.character(x[[2]]),]$name), as.character(name[name$id==as.character(x[[1]]),]$name), as.character(score[as.character(x[[2]]), as.character(x[[1]])]))}))
write.csv(output, 'data/kinship_dyad.csv', row.names=FALSE)
