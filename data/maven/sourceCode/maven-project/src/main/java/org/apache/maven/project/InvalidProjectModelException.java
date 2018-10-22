package org.apache.maven.project;

/*
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

import org.apache.maven.project.validation.ModelValidationResult;

public class InvalidProjectModelException
    extends ProjectBuildingException
{
    private final String pomLocation;

    private ModelValidationResult validationResult;

    public InvalidProjectModelException( String projectId, String pomLocation, String message, Throwable cause )
    {
        super( projectId, message, cause );
        this.pomLocation = pomLocation;
    }

    public InvalidProjectModelException( String projectId, String pomLocation, String message,
                                         ModelValidationResult validationResult )
    {
        super( projectId, message );

        this.pomLocation = pomLocation;
        this.validationResult = validationResult;
    }

    public InvalidProjectModelException( String projectId, String pomLocation, String message )
    {
        super( projectId, message );

        this.pomLocation = pomLocation;
    }

    public final String getPomLocation()
    {
        return pomLocation;
    }

    public final ModelValidationResult getValidationResult()
    {
        return validationResult;
    }

}