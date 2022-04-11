<?xml version="1.0" encoding="UTF-8"?>
<xsl:transform version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="text" encoding="UTF-8" byte-order-market="no" />
<xsl:template match="/pdml">
<xsl:for-each select="packet">
Timestamp:<xsl:value-of select="proto[@name='geninfo']/field[@name='timestamp']/@value" /> Data:<xsl:value-of select="proto[@name='fake-field-wrapper']/field[@name='data']/@value" />
</xsl:for-each>

</xsl:template>
</xsl:transform>
