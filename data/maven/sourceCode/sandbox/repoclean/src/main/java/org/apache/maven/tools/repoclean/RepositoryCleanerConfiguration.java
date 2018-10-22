package org.apache.maven.tools.repoclean;/*
 * Copyright 2001-2005 The Apache Software Foundation.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * @author jdcasey
 */
public class RepositoryCleanerConfiguration
{

    private String sourceRepositoryPath;

    private String sourceRepositoryLayout;

    private String targetRepositoryPath;

    private String targetRepositoryLayout;

    private String reportsPath;

    private boolean reportOnly;

    private String errorReportSubject;

    private String errorReportFromName;

    private String errorReportFromAddress;

    private String errorReportToName;

    private String errorReportToAddress;

    private String errorReportLink;

    private boolean mailErrorReport;

    private boolean force;

    private String blacklistedPatterns;

    private boolean reportWarningEnabled;

    private boolean convertSnapshots;

    public void setSourceRepositoryPath( String sourceRepositoryPath )
    {
        this.sourceRepositoryPath = sourceRepositoryPath;
    }

    public String getSourceRepositoryPath()
    {
        return sourceRepositoryPath;
    }

    public void setSourceRepositoryLayout( String sourceRepositoryLayout )
    {
        this.sourceRepositoryLayout = sourceRepositoryLayout;
    }

    public String getSourceRepositoryLayout()
    {
        return sourceRepositoryLayout;
    }

    public void setTargetRepositoryPath( String targetRepositoryPath )
    {
        this.targetRepositoryPath = targetRepositoryPath;
    }

    public String getTargetRepositoryPath()
    {
        return targetRepositoryPath;
    }

    public void setTargetRepositoryLayout( String targetRepositoryLayout )
    {
        this.targetRepositoryLayout = targetRepositoryLayout;
    }

    public String getTargetRepositoryLayout()
    {
        return targetRepositoryLayout;
    }

    public void setReportsPath( String reportsPath )
    {
        this.reportsPath = reportsPath;
    }

    public String getReportsPath()
    {
        return reportsPath;
    }

    public void setReportOnly( boolean reportOnly )
    {
        this.reportOnly = reportOnly;
    }

    public boolean reportOnly()
    {
        return reportOnly;
    }

    public void setErrorReportSubject( String errorReportSubject )
    {
        this.errorReportSubject = errorReportSubject;
    }

    public String getErrorReportSubject()
    {
        return errorReportSubject;
    }

    public String getErrorReportFromAddress()
    {
        return errorReportFromAddress;
    }

    public void setErrorReportFromAddress( String errorReportFromAddress )
    {
        this.errorReportFromAddress = errorReportFromAddress;
    }

    public String getErrorReportFromName()
    {
        return errorReportFromName;
    }

    public void setErrorReportFromName( String errorReportFromName )
    {
        this.errorReportFromName = errorReportFromName;
    }

    public String getErrorReportToAddress()
    {
        return errorReportToAddress;
    }

    public void setErrorReportToAddress( String errorReportToAddress )
    {
        this.errorReportToAddress = errorReportToAddress;
    }

    public String getErrorReportToName()
    {
        return errorReportToName;
    }

    public void setErrorReportToName( String errorReportToName )
    {
        this.errorReportToName = errorReportToName;
    }

    public void setMailErrorReport( boolean mailErrorReport )
    {
        this.mailErrorReport = mailErrorReport;
    }

    public boolean mailErrorReport()
    {
        return mailErrorReport;
    }

    public boolean force()
    {
        return force;
    }

    public void setForce( boolean force )
    {
        this.force = force;
    }

    public void setBlacklistedPatterns( String blacklistedPatterns )
    {
        this.blacklistedPatterns = blacklistedPatterns;
    }

    public String getBlacklistedPatterns()
    {
        return blacklistedPatterns;
    }

    public String getErrorReportLink()
    {
        return errorReportLink;
    }

    public void setErrorReportLink( String errorReportLink )
    {
        this.errorReportLink = errorReportLink;
    }

    public boolean isReportWarningEnabled()
    {
        return reportWarningEnabled;
    }

    public void setReportWarningEnabled( boolean reportWarningEnabled )
    {
        this.reportWarningEnabled = reportWarningEnabled;
    }

    public boolean isConvertSnapshots()
    {
        return convertSnapshots;
    }

    public void setConvertSnapshots( boolean convertSnapshots )
    {
        this.convertSnapshots = convertSnapshots;
    }
}