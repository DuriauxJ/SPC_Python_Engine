#control chart constants for n 2-25, imported from: https://www.bessegato.com.br/UFJF/resources/table_of_control_chart_constants_old.pdf 
#NaN added for n=1 so that index corresponds to n

CCC <- data.frame(
  A2 = c(NaN,1.880,1.023,0.729,0.577,0.483,0.419,0.373,0.337,0.308,0.285,0.266,0.249,0.235,0.223,0.212,0.203,0.194,0.187,0.180,0.173,0.167,0.162,0.157,0.153),
  A3 = c(NaN,2.659,1.954,1.628,1.427,1.287,1.182,1.099,1.032,0.975,0.927,0.886,0.850,0.817,0.789,0.763,0.739,0.718,0.698,0.680,0.663,0.647,0.633,0.619,0.606),
  d2 = c(NaN,1.128,1.693,2.059,2.326,2.534,2.704,2.847,2.970,3.078,3.173,3.258,3.336,3.407,3.472,3.532,3.588,3.640,3.689,3.735,3.778,3.819,3.858,3.895,3.931),
  D3 = c(NaN,0.000,0.000,0.000,0.000,0.000,0.076,0.136,0.184,0.223,0.256,0.283,0.307,0.328,0.347,0.363,0.378,0.391,0.403,0.415,0.425,0.434,0.443,0.451,0.459),
  D4 = c(NaN,3.267,2.574,2.282,2.114,2.004,1.924,1.864,1.816,1.777,1.744,1.717,1.693,1.672,1.653,1.637,1.622,1.608,1.597,1.585,1.575,1.566,1.557,1.548,1.541),
  B3 = c(NaN,0.000,0.000,0.000,0.000,0.030,0.118,0.185,0.239,0.284,0.321,0.354,0.382,0.406,0.428,0.448,0.466,0.482,0.497,0.510,0.523,0.534,0.545,0.555,0.565),
  B4 = c(NaN,3.267,2.568,2.266,2.089,1.970,1.882,1.815,1.761,1.716,1.679,1.646,1.618,1.594,1.572,1.552,1.534,1.518,1.503,1.490,1.477,1.466,1.455,1.445,1.435),
  c4 = c(NaN,0.798,0.886,0.921,0.940,0.952,0.959,0.965,0.969,0.973,0.975,0.978,0.979,0.981,0.982,0.983,0.985,0.985,0.986,0.987,0.988,0.988,0.989,0.989,0.990)
)





#----------sub-functions for CL()------------------------------------------------------------

#functions computing control limits and other relevant values for various control chart types:
#data returned, in order, by functions:
#Chart type, Lower control limit, Center line, Upper control limit, Individual standard deviation, Number of observations, Size of subgroups
MR <- function(data){
  MR <- abs(diff(data))
  cl <- mean(MR)
  lcl <- 0
  ucl <- CCC$D4[2] * cl
  sd <- cl/CCC$d2[2]
  
  return(list(
    type = "MR",
    lcl = lcl,
    cl = cl,
    ucl = ucl,
    sd = sd,
    m = length(MR),
    n = 2,
    values = as.vector(MR)))
}

I <- function(data, sd){
  cl  <- mean(data)
  lcl <- cl - 3 * sd
  ucl <- cl + 3 * sd
  
  return(list(
    type   = "I",
    lcl    = lcl,
    cl     = cl,
    ucl    = ucl,
    sd     = sd,
    m      = length(data),
    n      = 1,
    values = as.vector(data)))
}

R <- function(data){
  m <- nrow(data)
  n <- ncol(data)
  R <- apply(data,1,function(x) max(x)-min(x))
  cl <- mean(R)
  lcl <- CCC$D3[n]*cl
  ucl <- CCC$D4[n]*cl
  sd <- cl/CCC$d2[n]
  
  return(list(
    type = "R",
    lcl = lcl,
    cl = cl,
    ucl = ucl,
    sd = sd,
    m = m,
    n = n,
    values = R))
}

S <- function(data){
  m <- nrow(data)
  n <- ncol(data)
  S <- rep(0,m)
  for(i in 1:m){
    S[i] <- sqrt(var(data[i,]))
  }
  cl <- mean(S)
  lcl <- CCC$B3[n]*cl
  ucl <- CCC$B4[n]*cl
  sd <- cl/CCC$c4[n]
  
  return(list(
    type = "S",
    lcl = lcl,
    cl = cl,
    ucl = ucl,
    sd = sd,
    m = m,
    n = n,
    values = S))
}

X <- function(data, sd){
  m <- nrow(data)
  n <- ncol(data)
  xbar <- apply(data,1,mean)
  cl <- mean(xbar)
  lcl <- cl - 3 * sd/sqrt(n)
  ucl <- cl + 3 * sd/sqrt(n)
  
  return(list(
    type   = "X",
    lcl    = max(lcl,0),
    cl     = cl,
    ucl    = ucl,
    sd     = sd,
    m      = m,
    n      = n,
    values = xbar))
}

C <- function(data){
  defects <- data[,1]
  n <- data[1,2] #assumes n constant, checked beforehand in dispatcher function
  cl <- mean(defects)
  sd <- sqrt(cl)
  lcl <- cl - 3 * sd
  ucl <- cl + 3 * sd
  
  return(list(
    type   = "c",
    lcl    = max(lcl,0),
    cl     = cl,
    ucl    = ucl,
    sd     = sd,
    m      = length(defects),
    n      = data[1,2],
    values = defects))
}

u <- function(data){
  defects <- data[,1]
  m <- length(defects)
  n <- data[,2] 
  u <- defects/n
  cl <- sum(defects)/sum(n)
  sd_c <- function(n){sqrt(cl/n)}
  sd <- sd_c(n)
  lcl <- cl - 3 * sd
  ucl <- cl + 3 * sd
  
  return(list(
    type   = "u",
    lcl    = pmax(lcl,0),
    cl     = cl,
    ucl    = ucl,
    sd     = sd,
    m      = m,
    n      = n,
    values = u))
}

p <- function(data){
  defectives <- data[,1]
  m <- length(defectives)
  n <- data[,2] 
  p <- defectives/n
  cl <- sum(defectives)/sum(n)
  sd_p <- function(n){sqrt((cl*(1-cl))/n)}
  sd <- sd_p(n)
  lcl <- cl - 3 * sd
  ucl <- cl + 3 * sd
  
  return(list(
    type   = "p",
    lcl    = pmax(lcl,0),
    cl     = pmin(cl,1),
    ucl    = ucl,
    sd     = sd,
    m      = m,
    n      = n,
    values = p))
}

np <- function(data){
  defectives <- data[,1]
  m <- length(defectives)
  n <- data[1,2] #assumes n constant, checked beforehand in dispatcher function
  p <- sum(defectives)/(n*m)
  cl <- p*n
  sd <- sqrt(n*p*(1-p))
  lcl <- cl - 3 * sd
  ucl <- cl + 3 * sd
  
  return(list(
    type   = "np",
    lcl    = max(lcl,0),
    cl     = cl,
    ucl    = ucl,
    sd     = sd,
    m      = m,
    n      = n,
    values = defectives))
}

#functions automatically assigning control chart type if none specified:
auto_assign_CC_type <- function(data){
  if(is.vector(data) || ncol(data)==1){type <- "I-MR"}
  else if(ncol(data)<10){type <- "Xbar-R"}
  else {type <- "Xbar-S"}
  return(type)
}

auto_assign_CC_type_defects <- function(data){
  if(all(data[1,2]==data[1:nrow(data),2])){type <- "c"}
  else{type <- "u"}
  return(type)
}

auto_assign_CC_type_defectives <- function(data){
  if(all(data[1,2]==data[1:nrow(data),2])){type <- "np"}
  else{type <- "p"}
  return(type)
}





#----------CL() function----------------------------------------------------------------------

#uses the correct subfunctions to compute the control limits and other relevant informations, also chooses most relevant control chart type if none is specified
CL <- function(data, type="auto"){
  if(!is.numeric(data)){stop("provided data is not fully numeric")}
  if(!is.vector(data) && !is.matrix(data)){stop("provided data is not a vector or a matrix")}
  
  if(type=="auto"){type <- auto_assign_CC_type(data)}
  else if (type=="defects"){
    if(is.vector(data) || ncol(data)!=2){stop("defects require a 2 columns matrix to be processed")}
    type <- auto_assign_CC_type_defects(data)}
  else if (type=="defectives"){
    if(is.vector(data) || ncol(data)!=2){stop("defectives require a 2 columns matrix to be processed")}
    type <- auto_assign_CC_type_defectives(data)}
  
  #uses functions according to control chart type and returns 1 or 2 lists containing infos for further usage by other functions
  switch(type,
         "I-MR" = {
           if(!(is.vector(data)||ncol(data)==1)){stop("I chart requires a matrix with one column or a vector")}
           mr <- MR(data)
           i <- I(data,mr$sd)
           list(chart1 = i, chart2 = mr)
         },
         "Xbar-R" = {
           if(!is.matrix(data)||ncol(data)==1){stop("Xbar chart requires a matrix with more than one column")}
           r <- R(data)
           xbar <- X(data,r$sd)
           list(chart1 = xbar, chart2 = r)
         },
         "Xbar-S" = {
           if(!is.matrix(data)||ncol(data)==1){stop("Xbar chart requires a matrix with more than one column")}
           s <- S(data)
           xbar <- X(data,s$sd)
           list(chart1 = xbar, chart2 = s)
         },
         "c" = {
           if(!is.matrix(data) || ncol(data)!=2 || !all(data == floor(data)) || !all(data >= 0)){stop("c chart requires a 2-column matrix of whole positive numbers")}
           c_ <- C(data)
           list(chart1 = c_, chart2 = NULL)
         },
         "u" = {
           if(!is.matrix(data) || ncol(data)!=2 || !all(data == floor(data)) || !all(data >= 0)){stop("u chart requires a 2-column matrix of whole positive numbers")}
           U <- u(data)
           list(chart1 = U, chart2 = NULL)
         },
         "p" = {
           if(!is.matrix(data) || ncol(data)!=2 || !all(data == floor(data)) || !all(data >= 0)){stop("p chart requires a 2-column matrix of whole positive numbers")}
           if(!all(data[,1] <= data[,2])){stop("number of defectives can't exceed number of observations")}
           P <- p(data)
           list(chart1 = P, chart2 = NULL)
         },
         "np" = {
           if(!is.matrix(data) || ncol(data)!=2 || !all(data == floor(data)) || !all(data >= 0)){stop("np chart requires a 2-column matrix of whole positive numbers")}
           if(!all(data[,1] <= data[,2])){stop("number of defectives can't exceed number of observations")}
           NP <- np(data)
           list(chart1 = NP, chart2 = NULL)
         })}





#----------sub-functions for CC()------------------------------------------------------------

#functions returning the index of observations outside of control limits or following a suspicious pattern, works for a single chart:
detect_special_cause_single <- function(CL_output){
  values <- CL_output$values
  lcl <- CL_output$lcl
  ucl <- CL_output$ucl
  
  out_of_control_limits <- which(values>ucl | values<lcl,TRUE)
  if(is.matrix(out_of_control_limits)){out_of_control_limits <- as.vector(out_of_control_limits[,1])}
  
  trends_length <- rle(sign(diff(values)))$length
  trends_suspicious <- which(trends_length>5)
  trends <- integer(0)
  end_trends <- cumsum(trends_length)+1
  for(i in trends_suspicious){
    trends <- c(trends,(end_trends[i]-trends_length[i]):end_trends[i])
  }
  
  double_diff_rle <- rle(abs(diff(sign(diff(values)))))
  alternatings_suspicious <- which(double_diff_rle$values == 2 & double_diff_rle$length>12)
  alternatings <- integer(0)
  end_alternatings <- cumsum(double_diff_rle$length)+2
  for(i in alternatings_suspicious){
    alternatings <- c(alternatings,(end_alternatings[i]-double_diff_rle$length[i]):end_alternatings[i])
  }
  
  pattern <- unique(c(trends, alternatings))
  
  return(list(out_of_control_limits = out_of_control_limits, pattern = pattern, type = CL_output$type))
}

#applies detect_special_cause_single()
detect_special_cause <- function(CL_output){
  special_cause <- list()
  for(i in 1:length(CL_output)){
    if(is.null(CL_output[[i]])){break}
    special_cause[[i]] <- detect_special_cause_single(CL_output[[i]])
  }
  return(special_cause)
}

#function returning the full name of the inputed type as well as the legend of the y axis:
full_chart_name <- function(type){
  switch(type,
         "I" = c("Individuals control chart (I)","Individual Value"),
         "MR" = c("Moving Range control chart (MR)","Moving Range"),
         "S" = c("Standard Deviation control chart (S)","Standard Deviation"),
         "R" = c("Range control chart (R)","Range"),
         "X" = c("Sample Mean control chart (X̄)","Sample Mean"),
         "c" = c("Count control chart (c)","Number of Defects"),
         "u" = c("Defects per Unit control chart (u)","Defects per Unit"),
         "p" = c("Proportion Defective control chart (p)","Proportion Defective"),
         "np" = c("Number of Defectives control chart (np)","Number of Defectives"))
}

#function ploting a single control chart, highlighting special cause variation:
CC_single <- function(CL_output, SC){
  ucl <- CL_output$ucl
  lcl <- CL_output$lcl
  legend <- full_chart_name(CL_output$type)
  plot(CL_output$values, 
       type = "p",
       pch = 20, 
       cex = 1, 
       lwd = 2, 
       ylim = c(min(0.9*lcl,0.9*min(CL_output$values)),max(1.1*ucl,1.1*CL_output$values)),
       main = legend[1],
       ylab = legend[2],
       xlab = "")
  
  if (length(ucl) == 1) ucl <- rep(ucl, CL_output$m)
  if (length(lcl) == 1) lcl <- rep(lcl, CL_output$m)

  lines(ucl,col="red",type="l")
  lines(lcl,col="red",type="l")
  lines(CL_output$values, col = "black", lwd = 1)
  abline(h=CL_output$cl,col="blue",lty = 5)
  
  ocl <- SC[[1]]
  pat <- SC[[2]]
  if(!is.null(pat)){
    points(pat,CL_output$values[pat],col="darkorange",pch = 20,cex = 1.6)
    pat <- split(pat, cumsum(c(1, diff(pat) != 1)))
    for (i in pat) {
      if (length(i) > 1) {
        lines(i, CL_output$values[i],col = "darkorange",lwd = 1.5)
      }}}
  points(ocl,CL_output$values[ocl],col="red",pch = 20,cex = 1.6)}





#----------CC() function----------------------------------------------------------------------

#plot one or two control chart depending on the chart type, takes the output of CL as input
CC <- function(CL_output){
  SC <- detect_special_cause(CL_output)
  par(mar = c(3, 4, 2, 2))
  if(is.null(CL_output[[2]])){
    layout(matrix(1, nrow = 1, byrow = TRUE))
    CC_single(CL_output[[1]],SC[[1]])
  }
  else{
    layout(matrix(c(1, 2), nrow = 2, byrow = TRUE))
    CC_single(CL_output[[1]],SC[[1]])
    CC_single(CL_output[[2]],SC[[2]])
  }
}





#----------sub-functions for PC()------------------------------------------------------------

#returns TRUE if the process is stable
is.stable <- function(CL_output){
  sc <- detect_special_cause(CL_output)
  for(i in 1:length(sc)){
    if(length(sc[[i]]$out_of_control_limits)!=0 || length(sc[[i]]$pattern)!=0){return(FALSE)}
  }
  return(TRUE)
}
    




#----------PC() function----------------------------------------------------------------------

#determine process stability and capability based on CL() output and specification limits
PC <- function(CL_output,lsl,usl,target=1.33){
  if(!is.numeric(lsl)||!is.numeric(usl)){stop("specifications limits need to be numeric")}
  if(usl<=lsl){stop("upper specification limit needs to be greater than lower specification limit")}
  if(any(CL_output[[1]]$type==c("c","u","p","np"))){stop("impossible to compute Cp and Cpk for c,u,p or np chart due to normality assumption")}
  
  mean <- CL_output[[1]]$cl
  sd <- CL_output[[1]]$sd
  stable <- is.stable(CL_output)
  
  Cp <- (usl-lsl)/(6*sd)
  Cpk <- min((usl-mean)/(3*sd), (mean-lsl)/(3*sd))
  
  if (!stable) {status_text <- "The process is UNSTABLE, as such we cannot judge capability."} 
  else {
    if (Cpk >= target) {status_text <- paste("The process is STABLE and CAPABLE (Cpk =", round(Cpk, 2), ").")} 
    else {status_text <- paste("The process is STABLE but NOT CAPABLE (Cpk =", round(Cpk, 2), ").")}
  }
  
  return(list(stable = stable, Cp = Cp, Cpk = Cpk, status_text = status_text))
}





#----------sub-functions for SPC_Phase1()----------------------------------------------------------------------

#plots control charts along with a text stating stability and 
plot_with_text <-function(CL_output,lsl=NULL,usl=NULL,target=1.33){
  SC <- detect_special_cause(CL_output)
  par(mar = c(3, 4, 2, 2))
  
  if(any(CL_output[[1]]$type == c("c","u","p","np"))){
    layout(matrix(c(1, 1, 2), nrow = 3, byrow = TRUE), heights = c(0.425, 0.425,0.15))
    CC_single(CL_output[[1]],SC[[1]])
    if(is.stable(CL_output)){status_text <- "The process is STABLE"}
    else{status_text <- "The process is UNSTABLE"}
  }
  
  else if(any(is.null(c(lsl,usl)))){
    layout(matrix(c(1, 2, 3), nrow = 3, byrow = TRUE), heights = c(0.425, 0.425, 0.15))
    CC_single(CL_output[[1]],SC[[1]])
    CC_single(CL_output[[2]],SC[[2]])
    if(is.stable(CL_output)){status_text <- "The process is STABLE"}
    else{status_text <- "The process is UNSTABLE"}
  }
  
  else{
    layout(matrix(c(1, 2, 3), nrow = 3, byrow = TRUE), heights = c(0.425, 0.425, 0.15))
    CC_single(CL_output[[1]],SC[[1]])
    CC_single(CL_output[[2]],SC[[2]])
    status_text <- PC(CL_output,lsl,usl,target)$status_text
  }
  par(mar = c(0, 0, 0, 0))
  plot.new()
  text(0.5, 0.5, status_text, cex = 2.5, font = 2)
}





#----------SPC_Phase1() function----------------------------------------------------------------------

#combines the CL, CC and PC functions, omits capability if wrong type of chart or if no specification limits are entered, also returns the input from CL() for phase 2 monitoring
SPC_Phase1 <- function(data, lsl = NULL, usl = NULL, type = "auto", target = 1.33){
  CL_output <- CL(data,type)
  plot_with_text(CL_output,lsl,usl,target)
  return(CL_output)
}





#----------sub-function for SPC_Phase2()----------------------------------------------------------------------

#applies control limits built from phase 1 to new dataset
phase2_update_CL <- function(CL_output,CL_new){
  if(CL_new[[1]]$type == "u"){
    cl <- CL_output[[1]]$cl
    sd_c <- function(n){sqrt(cl/n)}
    CL_new[[1]]$sd <- sd_c(CL_new[[1]]$n)
    CL_new[[1]]$lcl <- pmax(cl - 3 * CL_new[[1]]$sd, 0)
    CL_new[[1]]$ucl <- cl + 3 * CL_new[[1]]$sd
    CL_new[[1]]$cl <- cl
    return(CL_new)
  }
  
  if(CL_new[[1]]$type == "p"){
    cl <- CL_output[[1]]$cl
    CL_new[[1]]$cl <- cl
    sd_p <- function(n){sqrt((cl*(1-cl))/n)}
    CL_new[[1]]$sd <- sd_p(CL_new[[1]]$n)
    CL_new[[1]]$lcl <- pmax(cl - 3 * CL_new[[1]]$sd, 0)
    CL_new[[1]]$ucl <- cl + 3 * CL_new[[1]]$sd
    return(CL_new)
  }
  
  CL_new[[1]]$lcl <- CL_output[[1]]$lcl
  CL_new[[1]]$cl <- CL_output[[1]]$cl
  CL_new[[1]]$ucl <- CL_output[[1]]$ucl
  
  if(!is.null(CL_new[[2]])){
    CL_new[[2]]$lcl <- CL_output[[2]]$lcl
    CL_new[[2]]$cl <- CL_output[[2]]$cl
    CL_new[[2]]$ucl <- CL_output[[2]]$ucl
  }
 
  return(CL_new)
}





#----------SPC_Phase2() function----------------------------------------------------------------------

#use control limits computed earlier with CL() and another dataset to plot control charts and check for stability
SPC_Phase2 <- function(CL_output,data,type="auto"){
  CL_new <- CL(data,type)
  if(CL_output[[1]]$type != CL_new[[1]]$type || !identical(CL_output[[2]]$type,CL_new[[2]]$type)){stop("The type of control charts are mismatched")}
  CL_new <- phase2_update_CL(CL_output,CL_new)
  plot_with_text(CL_new)
}




