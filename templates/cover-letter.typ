#let data = yaml(sys.inputs.at("data"))
#let p = data.profile
#let a = data.application
#let letter = a.letter
#let section-gap = 30pt
#set document(author: p.name, title: "Cover letter — " + p.name)
#set text(font: "Suisse Works", size: 11pt, lang: "en", region: "GB", ligatures: false)
#set page(
  paper: a.paper,
  margin: 22mm,
  footer: [
    #set text(size: 9pt, fill: rgb("#666666"))
    #link("mailto:" + p.email)[#p.email]
    #h(0.6em) | #h(0.6em)
    #link("tel:" + p.phone.replace(" ", ""))[#p.phone]
    #if letter.is_sample {
      linebreak()
      [LAYOUT SAMPLE — complete the bracketed text before use]
    }
  ],
)
#set align(left)
#set par(justify: false, leading: 0.65em, spacing: 12pt)

#p.name #h(1fr) #letter.formatted_date
#v(section-gap)
#block[#letter.recipient \ #letter.company]
#v(section-gap)
#strong("Application for " + letter.role)

Dear #letter.recipient,

#for paragraph in letter.paragraphs {
  block(above: 12pt, paragraph)
}

#v(10pt)
Yours faithfully,

#p.name
