<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="html" version="1.0" encoding="UTF-8"
		indent="yes" />
	<xsl:template match="/">
		<html>
			<STYLE type="text/css">
				@import "tests.css";
			</STYLE>
			<head>
				<script type="text/javascript" src="jquery.min.js" />
			</head>
			<body>
				<div id="testcasepage">
					<div id="title">
						<table>
							<tr>
								<td>
									<h1>TCT Report</h1>
								</td>
							</tr>
						</table>
					</div>
					<div id="summary">
						<table>
							<tr>
								<th colspan="2">Test Summary</th>
							</tr>
							<tr>
								<td>TCT Version</td>
								<td>
									<xsl:value-of select="result_summary/environment/@cts_version" />
								</td>
							</tr>
							<tr>
								<td>Test Plan Name</td>
								<td>
									<xsl:value-of select="result_summary/@plan_name" />
								</td>
							</tr>
							<tr>
								<td>Build</td>
								<td>
									To be implemented
								</td>
							</tr>
							<tr>
								<td>Test Total</td>
								<td>
									<xsl:value-of select="sum(result_summary//suite/total_case)" />
								</td>
							</tr>
							<tr>
								<td>Test Passed</td>
								<td>
									<xsl:value-of select="sum(result_summary//suite/pass_case)" />
								</td>
							</tr>
							<tr>
								<td>Test Failed</td>
								<td>
									<xsl:value-of select="sum(result_summary//suite/fail_case)" />
								</td>
							</tr>
							<tr>
								<td>Test Blocked</td>
								<td>
									<xsl:value-of select="sum(result_summary//suite/block_case)" />
								</td>
							</tr>
							<tr>
								<td>Test Not Executed</td>
								<td>
									<xsl:value-of select="sum(result_summary//suite/na_case)" />
								</td>
							</tr>
							<tr>
								<td>Time</td>
								<td>
									<xsl:value-of select="result_summary/summary/start_at" />
									~
									<xsl:value-of select="result_summary/summary/end_at" />
								</td>
							</tr>
						</table>
					</div>
					<div id="device">
						<table>
							<tr>
								<th colspan="2">Device Information</th>
							</tr>
							<tr>
								<td>Host Device</td>
								<td>
									<xsl:choose>
										<xsl:when test="result_summary/environment/@host">
											<xsl:if test="result_summary/environment/@host = ''">
												N/A
											</xsl:if>
											<xsl:value-of select="result_summary/environment/@host" />
										</xsl:when>
										<xsl:otherwise>
											N/A
										</xsl:otherwise>
									</xsl:choose>
								</td>
							</tr>
							<tr>
								<td>Device Name</td>
								<td>
									<xsl:choose>
										<xsl:when test="result_summary/environment/@device_name">
											<xsl:if test="result_summary/environment/@device_name = ''">
												N/A
											</xsl:if>
											<xsl:value-of select="result_summary/environment/@device_name" />
										</xsl:when>
										<xsl:otherwise>
											N/A
										</xsl:otherwise>
									</xsl:choose>
								</td>
							</tr>
							<tr>
								<td>Device Model</td>
								<td>
									<xsl:choose>
										<xsl:when test="result_summary/environment/@device_model">
											<xsl:if test="result_summary/environment/@device_model = ''">
												N/A
											</xsl:if>
											<xsl:value-of select="result_summary/environment/@device_model" />
										</xsl:when>
										<xsl:otherwise>
											N/A
										</xsl:otherwise>
									</xsl:choose>
								</td>
							</tr>
							<tr>
								<td>Device ID</td>
								<td>
									<xsl:choose>
										<xsl:when test="result_summary/environment/@device_id">
											<xsl:if test="result_summary/environment/@device_id = ''">
												N/A
											</xsl:if>
											<xsl:value-of select="result_summary/environment/@device_id" />
										</xsl:when>
										<xsl:otherwise>
											N/A
										</xsl:otherwise>
									</xsl:choose>
								</td>
							</tr>
							<tr>
								<td>Firmware Version</td>
								<td>
									<xsl:choose>
										<xsl:when test="result_summary/environment/@firmware_version">
											<xsl:if test="result_summary/environment/@firmware_version = ''">
												N/A
											</xsl:if>
											<xsl:value-of select="result_summary/environment/@firmware_version" />
										</xsl:when>
										<xsl:otherwise>
											N/A
										</xsl:otherwise>
									</xsl:choose>
								</td>
							</tr>
							<tr>
								<td>Screen Size</td>
								<td>
									<xsl:choose>
										<xsl:when test="result_summary/environment/@screen_size">
											<xsl:if test="result_summary/environment/@screen_size = ''">
												N/A
											</xsl:if>
											<xsl:value-of select="result_summary/environment/@screen_size" />
										</xsl:when>
										<xsl:otherwise>
											N/A
										</xsl:otherwise>
									</xsl:choose>
								</td>
							</tr>
							<tr>
								<td>Resolution</td>
								<td>
									<xsl:choose>
										<xsl:when test="result_summary/environment/@resolution">
											<xsl:if test="result_summary/environment/@resolution = ''">
												N/A
											</xsl:if>
											<xsl:value-of select="result_summary/environment/@resolution" />
										</xsl:when>
										<xsl:otherwise>
											N/A
										</xsl:otherwise>
									</xsl:choose>
								</td>
							</tr>
						</table>
					</div>


					<div id="suite_summary">
						<div id="title">
							<a name="contents"></a>
							<table>
								<tr>
									<td class="title">
										<h1>Test Summary by Suite</h1>
									</td>
								</tr>
							</table>
						</div>
						<table>
							<tr>
								<th>Suite</th>
								<th>Total</th>
								<th>Passed</th>
								<th>Failed</th>
								<th>Blocked</th>
								<th>Not Executed</th>
								<th class="Ratio">Ratio</th>
							</tr>
							<xsl:for-each select="result_summary/suite">
								<xsl:sort select="@name" />
								<tr class="suite_item">
								    <xsl:attribute name="id">
                                                <xsl:value-of select="@name" />
                                    </xsl:attribute>
									<td>
										<a>
											<xsl:attribute name="href"><xsl:value-of select="@name" />.xml</xsl:attribute>
											<xsl:value-of select="@name" />
										</a>
									</td>
									<td class="total">
										<xsl:value-of select="total_case" />
									</td>
									<td class="pass">
										<xsl:value-of select="pass_case" />
									</td>
									<td class="fail">
										<xsl:value-of select="fail_case" />
									</td>
									<td class="block">
										<xsl:value-of select="block_case" />
									</td>
									<td class="na">
										<xsl:value-of select="na_case" />
									</td>
									<td class="Ratio">
									    <div class="RatioGraphic" />
									</td>
								</tr>
							</xsl:for-each>
						</table>
					</div>

				</div>
				<div id="goTopBtn">
					<img border="0" src="./back_top.png" />
				</div>
				<script type="text/javascript" src="application.js" />
				<script language="javascript" type="text/javascript">
					$(document).ready(function(){
					goTopEx();
					drawRatio();
					});
				</script>
			</body>
		</html>
	</xsl:template>
	<xsl:template name="br-replace">
		<xsl:param name="word" />
		<xsl:variable name="cr">
			<xsl:text>
</xsl:text>
		</xsl:variable>
		<xsl:choose>
			<xsl:when test="contains($word,$cr)">
				<xsl:value-of select="substring-before($word,$cr)" />
				<br />
				<xsl:call-template name="br-replace">
					<xsl:with-param name="word" select="substring-after($word,$cr)" />
				</xsl:call-template>
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="$word" />
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
</xsl:stylesheet>
