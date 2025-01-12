export PATH="$PATH:« dotplate.vars.additional_paths|join(":") »"
export EDITOR=« dotplate.vars.editor »
⟨- if dotplate.vars.editor == 'vim' ⟩
export VISUAL=« dotplate.vars.editor »
⟨- endif ⟩
