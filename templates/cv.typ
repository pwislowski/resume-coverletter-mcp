#import "@preview/basic-resume:0.2.9": work
#import "theme.typ": theme
#let data = yaml(sys.inputs.at("data"))
#let p = data.profile
#let a = data.application
#show: theme.with(p, a.paper)

#for section in a.sections {
  heading(level: 2, upper(section))
  if section == "experience" {
    for job in p.experience {
      let bullets = job.achievements.filter(x => x.id in a.achievement_ids)
      if bullets.len() > 0 {
        block(breakable: false)[
          #work(title: job.title, company: job.company, dates: job.dates, location: job.location)
          #v(3pt)
          #list(..bullets.map(x => a.overrides.at(x.id, default: x.text)))
        ]
      }
    }
  } else if section == "projects" {
    for id in a.project_ids {
      let project = p.projects.find(x => x.id == id)
      block(breakable: false)[
        #strong(project.name) #if project.url != "" { h(1fr); text(size: 9pt, link(project.url)[#project.url.replace("https://", "")]) }
        #parbreak()
        #a.overrides.at(project.id, default: project.text)
      ]
    }
  } else if section == "skills" {
    for skill in p.skills {
      block(breakable: false)[#strong(skill.name + ":") #skill.text]
    }
  } else if section == "awards" {
    for award in p.awards { block(award) }
  } else if section == "education" {
    for entry in p.education {
      block(breakable: false)[#strong(entry.degree), #entry.institution #h(1fr) #entry.dates]
    }
  }
}
