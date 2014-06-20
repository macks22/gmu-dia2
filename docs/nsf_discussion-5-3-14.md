* our data:
    + one directorate (#5)
    + all data for that one directorate

* document vectors
    + cosine similarity is most common metric
        - use Jaccard similarity?
    + one for whole directorate
    + one for each division and program?
    + obviously do one for each PI

* divisions and programs (topic modelling)
    + can maybe serve as ground truth (classification label)
        - we know this award belongs to this division (given)
        - if we didn't know that, could we predict it
    + could be interesting and useful
    + might not work very well (unclear divisions)
    + worth experimenting with
    + we want to assign prob that PI is associated with division or program
        - one way is the above
        - another way is to find doc/term vec for each division
        - normalize doc/term for each division (how much does term x represent
          this division (number from 0 to 1))
        - categorical dist is vector of probs, where all probs must sum to 1
        - give it a word, it will tell you prob that you see word (given that
          categorical dist)
        - for this 1 PI, say the terms for this guy is 1000
        - you're doing 1000 draws from that division's categorical dist
        - what's prob that I get doc/term vector like this guy's PI?
        - could get fancier: what's prob terms for this person came from
          division A and B, but no others?
            ~ experiment and find best explanation for that PI's doc/term vector
            ~ MIXTURE of topics (from multiple distributions)
    + in practice:
        - take prob/mass function, plug in your observations
        - you have estimated params for that divisions categorical dist
        - directly calculate prob

* distributions
    + categorical (single-draw): bernoulli dist
    + multinomial (related to binomial)
        - always want to work with log probability

* topic modelling (LDA)
    + what subfields work together; who are key players?
    + can exploit basic text mining
    + doesn't allow a node to have high prob of being member of multiple
      communities
    + CESNA seems to believe they are better
        - referring mostly to heavily generative topic models

* CESNA
    + binary attributes and connections between people for comm detection
    + estimate multinomial dist for each community
    + topic model for each community
    + estimate term distribution
    + sum up and normalize all terms associated with all awardIDs for each comm
      CESNA finds

* Matt's work on comm detection (703-209-5044)
    + more directly relevant to DIA2 needs
    + directly estimate topic distributions (2nd step from CESNA)
    + can work on this more later (post-CESNA analysis)

* model:
    + person is part of one or more communities
    + each person has some association factor for each community

