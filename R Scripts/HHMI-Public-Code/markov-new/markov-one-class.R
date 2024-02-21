library(DiagrammeR)
library(dplyr)
library(DiagrammeRsvg)
library(magrittr)
library(rsvg)
#############################################################
#Edit the following
#############################################################
enroll.df<-read.csv("input-dataset/EnrollMatrix-Fake.csv", stringsAsFactors = F)
crs.sum<-read.csv("input-dataset/Class-Fake.csv", stringsAsFactors = F)

outfilename<-"Fake-One-Class"
title<-"Bio Majors - Fake Class"

last.sem<-5 # how many semesters

outplot.png<-paste('output-plots/markov-', outfilename, ".png")
outplot.pdf<-paste('output-plots/markov-', outfilename, ".pdf")

############################################################
# End Change
###########################################################
# Compute class state 

crs.df<-crs.sum



crs.states<-c("NT", "F", "P")
crs.states.num<-1:3


passing.grade<-2

for(i in 1:nrow(crs.df)){
  state<-1
  for(j in 1:ncol(crs.df)){
    if(j==1){
      if(crs.sum[i,j]>=passing.grade){
        crs.df[i,j]<-3
      }
      if(crs.sum[i,j]<passing.grade && crs.sum[i,j]>=0 ){
        crs.df[i,j]<-2
      }
      if(crs.sum[i,j]<0){
        crs.df[i,j]<-1
      }
    }
    else {
      if(crs.df[i,j-1]==1){
        if(crs.sum[i,j]>=passing.grade){
          crs.df[i,j]<-3
        }
        if(crs.sum[i,j]<passing.grade && crs.sum[i,j]>=0 ){
          crs.df[i,j]<-2
        }
        if(crs.sum[i,j]<0){
          crs.df[i,j]<-1
        }
        
      }
      if(crs.df[i,j-1]==2){
        if(crs.sum[i,j]>=passing.grade){
          crs.df[i,j]<-3
        }
        if(crs.sum[i,j]<passing.grade && crs.sum[i,j]>=0 ){
          crs.df[i,j]<-2
        }
        if(crs.sum[i,j]<0){
          crs.df[i,j]<-2
        }
      }
      # Passing course absorbing state
      if(crs.df[i,j-1]==3){
        crs.df[i,j]<-3
      }
    }
  }
}





#node types 1=class, 2=enroll

nodes<-data.frame(state=character(0), count=integer(0), state.num=integer(0), semester=integer(0), node.type=integer(0))
edges<-data.frame(state.i=character(0), state.f=character(0), count=integer(0), prob=double(0))

enroll.state<-c("EM", "ENM", "NE", "GDM", "GDNM")

node.count<-0
edge.count<-0



#
# Add terminal enrollment states
#

for(j in 1:last.sem){
  for(k in 2:length(enroll.state)){
    # Restrict to students enrolled as major in t
    reduced.en<-enroll.df[enroll.df[,j]==k,]
    if(nrow(reduced.en)==0) next
    state.i<-paste(enroll.state[k], j, sep="")
    node.count<-node.count+1
    nodes[node.count,]<-NA
    nodes$state[node.count]<-state.i
    nodes$count[node.count]<-nrow(reduced.en)
    
  }
}

#
# Add class enrollment states
#

for(j in 2:last.sem){
  for(k in 1:length(crs.states)){
    # Restrict to students enrolled as major
    reduced.en<-enroll.df[enroll.df[,j]==1,]
    reduced<-crs.df[enroll.df[,j]==1,]
    if(nrow(reduced.en)==0) next
    # Restrict to those in a certain class state
    reduced.crs<-reduced[reduced[,j-1]==k,]
    if(nrow(reduced.crs)==0) next
    state.i<-paste(enroll.state[1], crs.states[k], j, sep="")
    node.count<-node.count+1
    nodes[node.count,]<-NA
    nodes$state[node.count]<-state.i
    nodes$count[node.count]<-nrow(reduced.crs)
    
  }
}

#
# Add initial node
#

node.count<-node.count+1
nodes[node.count,]<-NA
nodes$state[node.count]<-paste(enroll.state[1], crs.states[1], 1, sep="")
nodes$count[node.count]<-nrow(enroll.df)

edge.count<-edge.count+1
edges[edge.count,]<-NA
edges$state.i[edge.count]<-"EMNT1"
edges$state.f[edge.count]<-"NT1"
cnt<-nrow(crs.df[crs.df[,1]==1,])
edges$count[edge.count]<-cnt
edges$prob[edge.count]<-cnt/nrow(enroll.df)


edge.count<-edge.count+1
edges[edge.count,]<-NA
edges$state.i[edge.count]<-"EMNT1"
edges$state.f[edge.count]<-"F1"
cnt<-nrow(crs.df[crs.df[,1]==2,])
edges$count[edge.count]<-cnt
edges$prob[edge.count]<-cnt/nrow(enroll.df)

edge.count<-edge.count+1
edges[edge.count,]<-NA
edges$state.i[edge.count]<-"EMNT1"
edges$state.f[edge.count]<-"P1"
cnt<-nrow(crs.df[crs.df[,1]==3,])
edges$count[edge.count]<-cnt
edges$prob[edge.count]<-cnt/nrow(enroll.df)




for(j in 1:last.sem){
  for(k in 1:length(crs.states.num)){
    cat("j", j, "k", k, "\n")
    # Transition from Course to Enrollment
    # Restrict to students enrolled as major in the semester
    reduced.en<-enroll.df[enroll.df[,j]==1,]
    reduced<-crs.df[enroll.df[,j]==1,]
    cat("student enrolled", k, nrow(reduced), nrow(reduced.en), "\n")
    if(nrow(reduced)==0)next
    #Find students in each course state
    reduced.crs<-reduced[reduced[,j]==k,]
    reduced.en.crs<-reduced.en[reduced[,j]==k,]
    cat("student in course state", k, nrow(reduced.crs), nrow(reduced.en.crs), "\n")
    if(nrow(reduced.crs)==0) next
    # Add course state node
    state.i<-paste(crs.states[k], j, sep="")
    node.count<-node.count+1
    nodes[node.count,]<-NA
    nodes$state[node.count]<-state.i
    nodes$count[node.count]<-nrow(reduced.crs)
    nodes$semester[node.count]<-j
    nodes$state.num[node.count]<-k
    nodes$node.type[node.count]<-1
    # Transition to next enrollment state
    if(j!=last.sem){
      next.sem<-j+1
      for(m in 1:length(enroll.state)){
        cat("m", m, "next.sem", next.sem, "\n")
        # Find student enrolled in each enrollment state next semester
        if(m>1){
          reduced.en.crs2<-reduced.en.crs[reduced.en.crs[,next.sem]==m,]
          reduced.crs2<-reduced.crs[reduced.en.crs[,next.sem]==m,]
          cat("student in enroll state next sem", m, nrow(reduced.crs2), nrow(reduced.en.crs2), "\n")
          # if none enrolled don't add edge
          if(nrow(reduced.en.crs2)==0) next
          #cat("Reduced2", m, nrow(reduced2), "\n")
          state.f<-paste(enroll.state[m], next.sem, sep="")
          edge.count<-edge.count+1
          edges[edge.count,]<-NA
          edges$state.i[edge.count]<-state.i
          edges$state.f[edge.count]<-state.f
          edges$count[edge.count]<-nrow(reduced.en.crs2)
          edges$prob[edge.count]<-nrow(reduced.crs2)/nrow(reduced.crs)
        }
        else { #m=1
          # Distinguish 3 enroll major states
          reduced.en.crs2<-reduced.en.crs[reduced.en.crs[,next.sem]==m,]
          reduced.crs2<-reduced.crs[reduced.en.crs[,next.sem]==m,]
          cat("student in enroll state next sem", m, nrow(reduced.crs2), nrow(reduced.en.crs2), "\n")
          # if none enrolled don't add edge
          if(nrow(reduced.en.crs2)==0) next
          #cat("Reduced2", m, nrow(reduced2), "\n")
          state.f<-paste(enroll.state[m], crs.states[k],  next.sem, sep="")
          edge.count<-edge.count+1
          edges[edge.count,]<-NA
          edges$state.i[edge.count]<-state.i
          edges$state.f[edge.count]<-state.f
          edges$count[edge.count]<-nrow(reduced.en.crs2)
          edges$prob[edge.count]<-nrow(reduced.crs2)/nrow(reduced.crs)
          
        }
      }
    }                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
    
  }
}

#
# Add nodes from enroll major to take
#

for(j in 2:last.sem){
  # Restrict to students enrolled as major in the semester
  reduced.en<-enroll.df[enroll.df[,j]==1,]
  reduced<-crs.df[enroll.df[,j]==1,]
  cat("student enrolled", k, nrow(reduced), nrow(reduced.en), "\n")
  for(m in 1:length(crs.states)){
    prev.sem<-j-1
    state.i<-paste(enroll.state[1], crs.states[m], j, sep="")
    reduced.crs.prev<-reduced[reduced[,prev.sem]==m,]
    reduced.en.crs.prev<-reduced.en[reduced[,prev.sem]==m,]
    if(nrow(reduced.crs.prev)==0) next
    cat("student enrolled with course state previous semester", m, nrow(reduced.crs.prev), nrow(reduced.en.crs.prev), "\n")
    #Loop over last semesters course state
    for(k in 1:length(crs.states.num)){
      cat("j", j, "m", m, "k", k, "\n")
      # find enrolled in class state
      reduced.crs<-reduced.crs.prev[reduced.crs.prev[,j]==k,]
      if(nrow(reduced.crs)==0) next
      #cat("Reduced2", m, nrow(reduced2), "\n")
      state.f<-paste(crs.states[k], j, sep="")
      edge.count<-edge.count+1
      edges[edge.count,]<-NA
      edges$state.i[edge.count]<-state.i
      edges$state.f[edge.count]<-state.f
      edges$count[edge.count]<-nrow(reduced.crs)
      edges$prob[edge.count]<-nrow(reduced.crs)/nrow(reduced.crs.prev)
      
    }
  }
}



#
# Remove zero nodes and edges
#

znodes<-subset(nodes, count==0)

nodes<-nodes[nodes$count>0,]
edges<-edges[which(edges$state.i %in% nodes$state),]
edges<-edges[which(edges$state.f %in% nodes$state),]









graph <-
  "digraph {
        rankdir=LR; // Left to Right, instead of Top to Bottom\n
        pad=0; // Space around figure
        nodesep=1; // spacing between nodes in a single semester
        ranksep=1;
        splines=false;
        label='All Bio Majors "

graph.end<-"    }
"

graph<-paste(graph, title, "';\n")

#
# Build graph
#

for(i in 1:nrow(nodes)){
  color="black"
  if(grepl("ENM", nodes$state[i]) || grepl("NE", nodes$state[i])) color<-"red"
  if(grepl("P", nodes$state[i])) color<-"green"
  if(grepl("F", nodes$state[i])) color<-"blue"
  graph<-paste(graph, nodes$state[i], " [shape=square, color='",color, "' label='", nodes$state[i],"\n", nodes$count[i], "' ];\n", sep="" )
}

graph<-paste(graph, "Legend [shape=square, color=purple, label='Enroll Major (EM)\n Enroll Non-Major (ENM)\n Not Enrolled (NE)\n Not Take (NT)\n Pass(P)\n Fail(F)\n EMF2 = Enroll Major Fail Sem 2'];\n")

#edge.test<-"EM1->EM2;\n"

for(i in 1:nrow(edges)){
  if(edges$count[i]>0 && edges$prob[i]>0.00)
    #graph<-paste(graph, edges$state.i[i], "->", edges$state.f[i],   ";\n", sep="" )
    #graph<-paste(graph, edges$state.i[i], "->", edges$state.f[i], "[label='", round(100*edges$prob[i],0),"']",   ";\n", sep="" )
    #graph<-paste(graph, edges$state.i[i], "->", edges$state.f[i], "[taillabel='", round(edges$prob[i],2),"']",   ";\n", sep="" )
    graph<-paste(graph, edges$state.i[i], "->", edges$state.f[i], "[taillabel=' ", round(100*edges$prob[i],0),"']",   ";\n", sep="" )
}

#graph<-paste(graph, edge.test, sep="")

graph<-paste(graph, graph.end, sep="")

#graph<-"digraph {\n        rankdir=LR; // Left to Right, instead of Top to Bottom\n
#  EM1 [shape=square, label='2767' ];
#  EM2 [shape=square, label='2767' ];
#  EM1->EM2;
#}"

gg<-grViz(graph)
print(gg)

grViz(graph) %>%
  export_svg %>% charToRaw %>% rsvg_pdf(outplot.pdf)
grViz(graph) %>%
  export_svg %>% charToRaw %>% rsvg_png(outplot.png)
#grViz(graph) %>%
#  export_svg %>% charToRaw %>% rsvg_svg("graph.svg")
