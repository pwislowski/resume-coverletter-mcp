#import "@preview/basic-resume:0.2.9": resume

#let body-font = "Suisse Intl"
#let label-font = "Suisse Works"

#let theme(person, paper, body) = {
  show heading.where(level: 1): set text(font: label-font)
  resume(
  author: upper(person.name),
  author-position: center,
  personal-info-position: center,
  phone: person.phone,
  email: person.email,
  linkedin: person.linkedin,
  personal-site: person.website,
  paper: paper,
  font: body-font,
  font-size: 10.5pt,
  accent-color: "#000000",
  {
    set par(justify: false, leading: 0.55em, spacing: 0.65em)
    set list(indent: 10pt, body-indent: 5pt, spacing: 4pt)
    show heading.where(level: 2): it => block(above: 12pt, below: 7pt)[
      #text(font: label-font, size: 10.5pt, weight: "bold", upper(it.body))
      #v(-5pt)
      #line(length: 100%, stroke: 0.5pt)
    ]
    body
  },
)
}
