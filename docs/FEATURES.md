# ContaAI Features

## Authentication

Status: Implementat

- Register
- Login
- Logout
- JWT access token
- Refresh token
- Cookie pentru refresh token
- Argon2 password hashing
- Identificarea utilizatorului curent

## Organizations

Status: Implementat

- Crearea organizațiilor
- Apartenența utilizatorilor la organizații
- Separarea datelor între organizații

## Companies

Status: Implementat

- Crearea companiilor
- Asocierea companiei cu organizația
- Cod fiscal
- Formă juridică
- Cod de țară

## Roles and Permissions

Status: Implementat

Roluri:

- Owner
- Administrator
- Accountant
- Auditor
- Employee

Permisiuni:

- organization.manage
- company.create
- company.read
- company.manage
- member.read
- member.manage
- document.read
- document.manage
- accounting.read
- accounting.manage
- report.read

## Public Infrastructure

Status: Implementat

Frontend:

`https://app-conta.bmobile.ro`

API:

`https://api-conta.bmobile.ro`

Swagger:

`https://api-conta.bmobile.ro/docs`

Cloudflare Tunnel:

`contaai-server`

## Document Inbox

Status: În dezvoltare

Planificat:

- Upload document
- MinIO storage
- Document metadata
- SHA-256 checksum
- Status processing
- Download securizat
- OCR
- AI extraction
- Human review

## Accounting Engine

Status: Planificat

Principii:

- Motor determinist
- AI-ul doar propune
- Aprobarea umană este obligatorie
- Debit egal cu credit
- Operațiunile sunt auditabile
