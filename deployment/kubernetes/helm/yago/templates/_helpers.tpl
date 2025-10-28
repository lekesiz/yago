{{/*
Expand the name of the chart.
*/}}
{{- define "yago.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "yago.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "yago.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "yago.labels" -}}
helm.sh/chart: {{ include "yago.chart" . }}
{{ include "yago.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "yago.selectorLabels" -}}
app.kubernetes.io/name: {{ include "yago.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Backend labels
*/}}
{{- define "yago.backend.labels" -}}
{{ include "yago.labels" . }}
app: yago
component: backend
{{- end }}

{{/*
Frontend labels
*/}}
{{- define "yago.frontend.labels" -}}
{{ include "yago.labels" . }}
app: yago
component: frontend
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "yago.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "yago.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Backend service name
*/}}
{{- define "yago.backend.serviceName" -}}
{{- printf "%s-backend" (include "yago.fullname" .) }}
{{- end }}

{{/*
Frontend service name
*/}}
{{- define "yago.frontend.serviceName" -}}
{{- printf "%s-frontend" (include "yago.fullname" .) }}
{{- end }}
