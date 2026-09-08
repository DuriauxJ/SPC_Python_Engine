source("C:/Users/User/Desktop/SPC/Joakim_Duriaux_SPC_Main.R") #ENTER CORRECT FILE PATH

#----------data generating functions----------------------------------------------------------------------

gen_variable <- function(m, n, mean = 100, sd = 10, percent_special_cause = 0.05, entire.row = TRUE) {
  obs <- matrix(rnorm(m * n, mean, sd ), m, n)
  
  if(percent_special_cause>0){
    if(entire.row){
      n_sc <- ceiling(m * percent_special_cause)
      sc_rows <- sample(1:m, n_sc)
      shifts <- sample(c(-1, 1), n_sc, replace = TRUE) * runif(n_sc, 4, 6) * sd
      obs[sc_rows, ] <- obs[sc_rows, ] + shifts
    }
    else{  
      n_sc <- ceiling(m * n * percent_special_cause)
      sc_rows <- sample(1:m, n_sc, replace = TRUE)
      sc_cols <- sample(1:n, n_sc, replace = TRUE)
      indices <- cbind(sc_rows, sc_cols)
      obs[indices] <- obs[indices] + sample(c(-1, 1), n_sc, replace = TRUE) * runif(n_sc, 4, 6) * sd}
  }
  return(obs)
}





gen_defects <- function(m, n = 50, rate = 0.1, percent_special_cause = 0.05) {
  if (length(n) == 1) {n_sampled <- rep(n, m)} 
  else {n_sampled <- sample(n, m, replace = TRUE)}
  
  defects <- rpois(m, rate * n_sampled)
  
  if(percent_special_cause>0){
    n_sc <- ceiling(m * percent_special_cause)
    sc_rows <- sample(1:m, n_sc)
    sc_rates <- rate * runif(n_sc, 3, 5)
    defects[sc_rows] <- rpois(n_sc, lambda = sc_rates * n_sampled[sc_rows])
  }
  return(cbind(defects, n_sampled))
}





gen_defectives <- function(m, n = 50, p = 0.02, percent_special_cause = 0.05) {
  if (length(n) == 1) {n_sampled <- rep(n, m)} 
  else {n_sampled <- sample(n, m, replace = TRUE)}
  
  defectives <- rbinom(m, n_sampled, p)
  
  if(percent_special_cause>0){
    n_sc <- ceiling(m * percent_special_cause)
    sc_rows <- sample(1:m, n_sc)
    sc_probs <- pmin(p * runif(n_sc, 3, 10), 1)
    defectives[sc_rows] <- rbinom(n_sc, size = n_sampled[sc_rows], prob = sc_probs)
  }
  return(cbind(defectives, n_sampled))
}





#----------example control charts----------------------------------------------------------------------
SPC_Phase1(gen_variable(20,1,percent_special_cause=0)) #I-MR
SPC_Phase1(gen_variable(20,1)) #I-MR with special cause

SPC_Phase1(gen_variable(20,5,percent_special_cause=0)) #Xbar-R
SPC_Phase1(gen_variable(20,5)) #Xbar-R with special cause

SPC_Phase1(gen_variable(20,15,percent_special_cause=0)) #Xbar-S
SPC_Phase1(gen_variable(20,15)) #Xbar-S with special cause

SPC_Phase1(gen_defects(20,50,percent_special_cause=0),type="defects") #c
SPC_Phase1(gen_defects(20,50),type="defects") #c with special cause

SPC_Phase1(gen_defects(20,30:70,percent_special_cause=0),type="defects") #u
SPC_Phase1(gen_defects(20,30:70),type="defects") #u with special cause

SPC_Phase1(gen_defectives(20,50,percent_special_cause=0),type="defectives") #np
SPC_Phase1(gen_defectives(20,50),type="defectives") #np with special cause

SPC_Phase1(gen_defectives(20,30:70,percent_special_cause=0),type="defectives") #p
SPC_Phase1(gen_defectives(20,30:70),type="defectives") #p with special cause



#----------example capability----------------------------------------------------------------------
SPC_Phase1(gen_variable(20,15,percent_special_cause=0),lsl=50,usl=150)

#----------example phase 2 monitoring----------------------------------------------------------------------
A <- SPC_Phase1(gen_variable(20,5,percent_special_cause=0)) #setup / phase 1

SPC_Phase2(A, gen_variable(20,5,percent_special_cause=0)) #same distribution
SPC_Phase2(A, gen_variable(20,5,percent_special_cause=0.05)) #same distribution, special cause
SPC_Phase2(A, gen_variable(30,7,percent_special_cause=0)) #same distribution, different n and m
SPC_Phase2(A, gen_variable(20,5,mean=115,percent_special_cause=0)) #different distribution


B <- SPC_Phase1(gen_defectives(20,30:70,percent_special_cause=0), type="defectives")

SPC_Phase2(B, gen_defectives(25,50:100,percent_special_cause=0), type="defectives") #phase 2 monitoring also works with copntrol limits depending on n




