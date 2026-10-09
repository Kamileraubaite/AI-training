# Banking Complaints Intelligence API for a financial firm 

The aim of this project is to help benking staff review complaints, 
search relevant documents for support, and also generate draft AI guidance.

All customer records and policy documents are synthetic.
AI outputs also require staff review.

## Relevance floor

I chose a relevance floor of 0.45 after testing out different thresholds and seeing how 
they differ when being asked multiple different banking complaint questions and 
irrelivent questions.

A floor of 0.50 excluded the relevant Complaint Handling Policy,
which scored 0.475. At 0.45, this policy was included, while an
unrelated chocolate-cake question was still refused.

This is a starting threshold based on a small set of questions¡
