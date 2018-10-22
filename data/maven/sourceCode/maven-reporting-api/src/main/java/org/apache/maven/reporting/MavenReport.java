package org.apache.maven.reporting;

/*
 * Copyright 2005 The Apache Software Foundation.
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

import org.apache.maven.model.Model;
import org.codehaus.doxia.sink.Sink;

/**
 * The basis for a Maven report.
 *
 * @author Brett Porter
 * @version $Id$
 */
public interface MavenReport
{
    String ROLE = MavenReport.class.getName();

    /** @todo don't want the model here long term. */
    void execute( Model model, Sink sink )
        throws MavenReportException;

    String getOutputName();
}