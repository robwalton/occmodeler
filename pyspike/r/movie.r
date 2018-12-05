args = commandArgs(trailingOnly=TRUE)
if (length(args)!=7) {
  stop("6 arguments expected", call.=FALSE)
}

places_path<-args[1]
gml_path <- args[2]
start <- as.numeric(args[3])
stop <- as.numeric(args[4])
step <- as.numeric(args[5])
scale <- as.numeric(args[6])
out_path <- args[7]  # should end in mp4 !
print(paste0("places_path: ", places_path))
print(paste0("gml_path: ", gml_path))
print(paste0("start: ", start))
print(paste0("stop: ", stop))
print(paste0("step: ", step))
print(paste0("scale: ", scale))
print(paste0("out_path: ", out_path))


library("animation") 
library("igraph")
library("RColorBrewer")


library(tidyverse)


load_spike_csv <- function(places_path, kind) { 
  

  raw_nodes <- read_delim(places_path, ";")
  
  nodes <- raw_nodes %>%
    gather(node, count, -Time) %>%
    separate(node, into = c("name", "num"), "sep" = "_(?!.*_)", fill = "right", extra = "merge")  %>%
    rename(time = "Time") %>%
    add_column(kind=kind, .after="time")
  
  nodes$num <- as.integer(nodes$num)
  
  return(nodes)
}


movie_for_Y_abcC_v2 <- function(start, stop, step, scale, places_path, net) {
  
  add_alpha <- function(rgb) {
    return(grDevices::adjustcolor(rgb, alpha=0.5))
  }
  places <- load_spike_csv(places_path, 'place')
  places <- filter(places, name %in% c("a", "b", "c", "C"))
  places <- filter(places, !is.na(num))
  places$num <- as.integer(places$num)
  layout <- layout_with_fr(net)
  ani.options(convert="/usr/local/bin/magick")
  
  saveVideo({
    for (t in seq(start, stop-step, step)) {
      places_t <- places %>% filter(near(time, t, tol=0.001)) %>% arrange(num) 
      
      a_counts = places_t %>% filter(name=="a") %>% pull(count)
      b_counts = places_t %>% filter(name=="b") %>% pull(count)
      c_counts = places_t %>% filter(name=="c") %>% pull(count)
      cbar_counts = places_t %>% filter(name=="C") %>% pull(count)
      print(t)
      rbg <- brewer.pal(3, "Set1")
      red = add_alpha(rbg[1])
      green = add_alpha(rbg[3])
      blue = add_alpha(rbg[2])
      
      #      V(net)$size <- sqrt(a_counts) * scale
      #      plot(net, layout=layout, xlim=c(-2, 2), ylim=c(-2, 2), vertex.color=pal[1])
      V(net)$size <- sqrt(b_counts) * scale
      plot(net, layout=layout, xlim=c(-2, 2), ylim=c(-2, 2), vertex.color=blue)
      V(net)$size <- sqrt(c_counts) * scale
      plot(net, layout=layout, xlim=c(-2, 2), ylim=c(-2, 2), vertex.color=red, add=TRUE)
      V(net)$size <- sqrt(cbar_counts) * scale
      plot(net, layout=layout, xlim=c(-2, 2), ylim=c(-2, 2), vertex.color=green, add=TRUE)
    }
  }, interval = 0.2, video.name=out_path, nmax=500, ani.width=1024,ani.height=1024)
  
}

net <- read_graph(gml_path, "gml")
movie_for_Y_abcC_v2(start, stop, step, scale, places_path, net)