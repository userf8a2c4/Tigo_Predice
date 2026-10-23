# Fuentes públicas y supuestos

Cada supuesto de `config/negocio.toml` está marcado como **"supuesto a validar"**, **"benchmark público"** o **"dato Tigo"**. Estas son las fuentes públicas usadas para fijar órdenes de magnitud. Todas deben validarse con Tigo.

## Efecto de los avisos proactivos de falla
- **MidSouth Fiber (Calix/GLDS, 2024):** en una falla que afectó a 99 suscriptores, llamó el 4 % de los que tenían alertas por SMS, frente al 33 % de los que no. La muestra es pequeña y la fuente es de un proveedor. → Se usa como **benchmark de tasa de llamada sin aviso (33 %)**.
  https://www.calix.com/blog/2024/11/transform-network-outage-management.html
- **Convey (2026, empresa eléctrica):** −57 % de tráfico al contact center con comunicación proactiva en cortes programados. No es una telecom.
  https://www.goconvey.com/how-proactive-communication-reduced-call-center-volume-by-57-during-public-safety-power-shutoffs/
- **KUBRA (cliente eléctrico):** −18 % de llamadas entrantes.
  https://sumeru.us/blog/why-are-your-customers-still-calling
- **TEC (Adtran/GOCare, 2026):** menos tickets con avisos de falla, sin porcentaje publicado.
- → **Rango usado para la reducción: 10 % / 20 % / 35 %.** Es conservador frente a los benchmarks porque todos vienen de proveedores.

## Costo de WhatsApp Business
- Plantilla de **utilidad**, Resto de Latinoamérica: **≈ US$0.0113 por mensaje** (tarifa del 1-jul-2026, según Zernio, fuente secundaria). Las plantillas de utilidad dentro de la ventana de atención son gratuitas, pero los avisos proactivos se envían fuera de ella. **Verificar** con https://developers.facebook.com/docs/whatsapp/pricing

## Tamaño de la base
- Tigo Honduras: **~5.0 M de clientes móviles** y **~175 mil de hogar** (Millicom, Form 20-F 2025).
  https://www.sec.gov/Archives/edgar/data/912958/000162828026020831/tigo-20251231.htm
- Tigo tenía el 66 % de las líneas móviles en el primer trimestre de 2025, según CONATEL vía DPL News.

## Costo por llamada
- Agente de LATAM nearshore: US$12–24 por hora todo incluido (FusionCX, Retell AI, 2026). Con ~8 llamadas efectivas por hora, sale ≈ US$3.15, unos **L 85**. Supuesto a validar con Finanzas.

## Tipo de cambio
- ≈ **L 27 por US$** (BCH, octubre 2026).

## ¿Ya existe en Millicom/Tigo?
- No se encontró evidencia pública de avisos proactivos de fallas por WhatsApp de Tigo/Millicom. Hay que confirmarlo internamente.

## Frente Hogar (v03)
- **Comcast/Xfinity** identifica a los clientes afectados y les envía textos proactivos durante las fallas (testimonio ante el Senado de Vermont, 26-mar-2024).
  https://legislature.vermont.gov/Documents/2024/WorkGroups/Senate%20Government%20Operations/Bills/S.310/Witness%20Documents/S.310~Jim%20White~Comcast%20Practices%20on%20Notices%20and%20Information%20Provided%20to%20Customers~3-26-2024.pdf
- **AT&T** ofrece alertas por texto de restablecimiento del servicio de internet y TV (att.com/outages; nota de KTRK, mayo de 2024).
- **Ksolves** (caso de un operador de cable anónimo): IA sobre telemetría DOCSIS, **−60 % de visitas innecesarias**. Cifra del proveedor.
  https://www.ksolves.com/case-studies/big-data/predictive-cable-network-analytics-platform-docsis
- **Beegol:** agentes de IA para diagnóstico remoto, **hasta −20 % de visitas** y −40 % de llamadas técnicas. Material comercial, sin cliente identificado.
  https://beegol.com
- Usamos el extremo bajo: el caso base equivale a **6 % menos del total de visitas**.

## Protección de datos y seguridad
- Honduras no tiene ley integral de datos personales; el proyecto está pendiente en el Congreso desde 2018.
  https://www.dlapiperdataprotection.com/index.html?c=HN&t=law ·
  https://www.elheraldo.hn/honduras/iaip-destaca-beneficios-honduras-ley-proteccion-datos-personales-BP26294115
- Habeas data (art. 182, reforma por Decreto 10-2013): https://oncae.gob.hn/wp-content/uploads/2024/05/Decreto-10-2013.pdf
- Detalle y marcos internacionales (GDPR, ISO 27001/27701/42001, SOC 2, NIST, OWASP, MITRE ATLAS): [seguridad_y_privacidad.md](seguridad_y_privacidad.md).
